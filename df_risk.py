import pandas as pd
import random, os
import matplotlib.pyplot as plt
from risk_defs import *

class Expanse (set):
    
    def __init__(self, a=set()):
        self.update(a)
        
    def __repr__(self):
        return 'Expanse({l})'.format(l=', '.join([region_names[r] for r in self]))
        
    def border(self):
        """ Return an Allocation of the neigboring Regions which are not in this Allocation. """
        return self.complement().external()
    
    def complement(self):
        """ Return an Expanse containing all regions which are not in this Expanse. """
        return Expanse(self.world().difference(self))

    @classmethod
    def continent(cls, c):
        """ Return an Expanse containing all regions in continent c. Accepts continent indices
            as well as names. """
        if type(c) == int:
            return cls(continent_regions[c])
        else:
            for idx, name in continent_names.items():
                if name == c:
                    return cls.continent(int(idx))
            raise Exception('unknown continent: {c}'.format(c=c))
            
    def continent_bonus(self):
        """ Return the reinforcement bonus for the Expanse. """
        return sum([continent_bonuses[c] for c in self.full_continents()])
    
    def distant(self):
        """ Return an Allocation of all regions which are not in and do not border this Allocation. """
        return self.complement().internal()    
    
    def external(self):
        """ Return all regions of the Expanse which do border with regions outside the Expanse. """
        return Expanse([r for r in self if (len(set(region_neighbors[r]).difference(self)) > 0)])    
    
    def full_continents(self):
        """ Return a list of all continents this Expanse contains. """
        return [c for c in range(6) if self.continent(c).issubset(self)]
    
    def internal(self):
        """ Return all regions of the Expanse which do not border with any regions outside the Expanse. """
        return Expanse([r for r in self if (len(set(region_neighbors[r]).difference(self)) == 0)])    

    def plot(self, color='black'):
        """ Plot the Expanse. """
        im = plt.imread(os.getcwd() + '/risk.png')
        plt.figure(figsize=(10, 15))
        implot = plt.imshow(im)
        for region in self:
            coor = region_locations[region]
            plt.scatter([coor[0]], [coor[1]], s = 300, c=color)
        plt.show()
    
    def reinforcements(self):
        """ Return the number of reinforcements this Expanse grants. """
        return max(3, len(self)/3) + self.continent_bonus()
    
    @classmethod
    def world(cls):
        """ Return an Expanse of all regions. """
        return cls(range(42))    
    

class RiskBoard (object):
    
    def __init__(self, game_id, players):
        self._create_df(game_id, players) 
        
    def _create_df(self, game_id, players):
        self.df = pd.DataFrame({
            'game_id'    : [game_id]*42,
            'turn'       : [-1]*42,
            'region'     : range(42),
            'owner'      : [-1]*42,
            'armies'     : [1]*42
        })
        self._add_continents()
        self._distribute(players)
    
    def _add_continents(self):
        """ Add a column containing the continents to the df. """
        self.df['continent'] = [region_continents[region] for region in self.df.region]
    
    @staticmethod
    def _checkEqual(x):
        x = list(x.values)
        if len(x) == 0: return None
        if x.count(x[0]) == len(x):
            return x[0]
        else:
            return None
    
    def _distribute(self, players):
        """ Distribute all regions over the players. """
        while len(self._neutral_regions()) > 0:
            for player in players:
                neutral_regions = self.df[self.df.owner == -1].region.values
                if len(neutral_regions) == 0: break
                region = random.choice(neutral_regions)
                self._set_owner(region, player.player_id)

    def armies(self, player_id):
        """ Return the total number of armies owned by the player with `player_id`. """
        return self.df[self.df.owner == player_id].armies.sum()

    def game_id(self):
        """ Return the game_id. """
        return self.df.game_id.loc[0]
    
    def regions(self, player_id):
        """ Return an Expanse of regions owned by the player with `player_id`. """
        return Expanse(self.df[self.df.owner == player_id].regions.values) 

    def turn(self):
        """ Return the current turn. """
        return self.df.turn.max()   

    


    def next_turn(self):
        self.df.turn = self.turn()+1
    
    def place(self, region, n_armies=1):
        old_armies = self.df[self.df.region == region].armies.sum()
        self._set_armies(region, old_armies+n_armies)


    
    def _set_armies(self, region, armies):
        self.df.loc[self.df[self.df.region == region].index, 'armies'] = armies

    def _set_owner(self, region, owner):
        self.df.loc[self.df[self.df.region == region].index, 'owner'] = owner
        
    def plot(self):
        im = plt.imread(os.getcwd() + '/risk.png')
        plt.figure(figsize=(10, 15))
        implot = plt.imshow(im)
        for region, owner, armies in zip(self.df.region, self.df.owner, self.df.armies):
            self.plot_single(region, owner, armies)
        plt.show()
        
    def plot_single(self, region, owner, armies):
        coor = self.region_locations[region]
        plt.scatter([coor[0]], [coor[1]], s = 300, c=self.color[owner])
        plt.text(coor[0], coor[1]+12, s=str(armies), 
                 color='black' if self.color[owner] == 'yellow' else 'white',
                 ha='center', size='x-large')
        


class RiskCards (object):
    
    def __init__(self, game_id, players):
        pass
    
    def next_turn(self):
        pass
    
class RiskGame (object):
    
    def __init__(self, game_id, players):
        self.players = players
        self.board   = RiskBoard(game_id, players)
        self.cards   = RiskCards(game_id, players)
        
    def __repr__(self):
        return 'RiskGame({id}, turn={turn}, player={player})'.format(
            id=self.board.game_id(),
            turn=self.turn(),
            player=self.current_player())
     
    def attack(self):
        pass
        
    def current_player(self):
        """ Return the player whose turn is the current. """
        player_index = self.turn() % self.n_players()
        return self.players[player_index]
    
    def fortify(self):
        pass
    
    def initial_place(self):
        while True:
            changed = False
            for player in self.players:
                if self.board.armies(player.player_id) < self.starting_armies():
                    region = player.place(self.board)
                    self.board.place(region, 1)
                    changed = True
            if not changed: break
     
    def n_players(self):
        """ Return the number of players. """
        return len(self.players)
    
    def play_turn(self):
        self.reinforce()
        self.attack()
        self.fortify()
        self.board.next_turn()
        self.cards.next_turn()
    
    def reinforce(self):
        for i in range(self.board.reinforcements(self.current_player().player_id)):
            region = self.current_player().place(self.board)
            self.board.place(region, 1)
        # TODO: do something with the cards
    
    def starting_armies(self):
        if len(self.players) == 3:
            return 35
        elif len(self.players) == 4:
            return 30
        elif len(self.players) == 5:
            return 25
        elif len(self.players) == 6:
            return 20
        else:
            raise Exception('no rules for starting a game with {n} players'.format(n=len(self.players)))
       
    def turn(self):
        """ Return the current turn. """
        return self.board.turn()
    
class RiskPlayer (object):
    
    def __init__(self, player_id):
        self.player_id = player_id
        
    def __repr__(self):
        return '{name}({id})'.format(name=self.__class__.__name__, id=self.player_id)
        
    def place(self, board):
        regions = board.regions(self.player_id)
        return random.choice(regions)
    
class RiskStuff (object):
    
    def __init__(self, game_id, n_players):
        self.game_id = game_id
        self.n_players = n_players
        self.board_df = self._init_board_df(0)
        self.card_df  = self._init_card_df(0)
        

    
    def _init_card_df(self, turn):
        return pd.DataFrame({
            'record_type': ['card']*self.n_players,
            'turn'       : [turn]*self.n_players,
            'game_id'    : [self.game_id]*self.n_players,
            'owner'      : range(self.n_players),
            'inf_card'   : [0]*self.n_players,
            'cav_card'   : [0]*self.n_players,
            'can_card'   : [0]*self.n_players
        })
                
       
        
        