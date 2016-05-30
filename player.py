import random
import definitions, missions

class Player (object):
    
    def __init__(self, name=None):
        self.name      = name
        self.player_id = None
        
    @property
    def description(self):
        return self.__class__.__name__
    
    @property
    def color(self):
        return definitions.player_color[self.player_id]
    
    def mission(self, game):
        return game.missions[self.player_id]
    
    def attack(self, b):
        raise Exception('base player cannot play')
    def fortify(self, b):
        raise Exception('base player cannot play')
    def place(self, b):
        raise Exception('base player cannot play')        

class RandomPlayer (Player):
    
    def attack(self, game):
        if random.random() > 0.90 and game.board.n_armies(self.player_id) < 50:
            return None
        possible_attacks = game.board.possible_attacks(self.player_id)
        if len(possible_attacks) == 0:
            return None
        attack = random.choice(possible_attacks)
        return attack[0], attack[2], attack[1]-1

    def fortify(self, game):
        possible_fortifications = game.board.possible_fortifications(self.player_id)
        if len(possible_fortifications) == 0:
            return None
        fortification = random.choice(possible_fortifications)
        return fortification[0], fortification[2], random.randint(1, fortification[1]-1)

    def place(self, game):
        return random.choice(list(game.board.territories_of(self.player_id)))
    
    def use_cards(self, game):
        co, obl = game.card_options(self.player_id)
        if obl or (any(co) and random.random() > 0.5):
            return random.choice([i for i, x in enumerate(co) if x])
        return None

        
    
class RuleBasedPlayer (RandomPlayer):

    @staticmethod
    def attack_score(fr_tid, fr_arm, to_tid, to_pid, to_arm):
        return float(fr_arm-1) / to_arm

    @staticmethod
    def vantage(game, territory_id):
        own_armies = game.board.armies(territory_id)
        htl_armies = sum([arm for tid, pid, arm in game.board.hostile_neighbors(territory_id)])
        return float(own_armies) / (htl_armies+0.01)

    def attack(self, game):
        possible_attacks = game.board.possible_attacks(self.player_id)
        if len(possible_attacks) == 0:
            return None

        attack = max(possible_attacks, key=lambda x: self.attack_score(*x))
        if self.attack_score(*attack) < 1:
            return None

        return attack[0], attack[2], attack[1]-1

    def vantage_ratio(self, game, from_territory_id, to_territory_id):
        return self.vantage(game, from_territory_id)/self.vantage(game, to_territory_id)
    
    #def place(self, game):
    #    options = [(tid, self.vantage(game, tid)) 
    #            for tid in game.board.territories_of(self.player_id)]
    #    return min(options, key=lambda x: x[1])[0]
    
    #def fortify(self, game):
    #    possible_fortifications = game.board.possible_fortifications(self.player_id)
    #    if len(possible_fortifications) == 0:
    #        return None
    #    fort = max(possible_fortifications, key=lambda x: self.vantage_ratio(game, x[0], x[2]))
    #    return fort[0], fort[2], fort[1]-1
    
    def use_cards(self, game):
        co, obl = game.card_options(self.player_id)
        choices = [i for i, x in enumerate(co) if x]
        if obl:
            return max(choices)
        elif 3 in choices:
            return 3
        else:
            return None
        
class FortifyingPlayer (RuleBasedPlayer):
    
    @staticmethod
    def territory_vantage(game, territory_id):
        hn_count = len(list(game.board.hostile_neighbors(territory_id)))
        fn_count = len(list(game.board.friendly_neighbors(territory_id)))
        return float(fn_count) / (0.01 + hn_count)
    
    @classmethod
    def territory_vantage_ratio(cls, game, from_territory_id, to_territory_id):
        return cls.territory_vantage(game, from_territory_id) / \
               cls.territory_vantage(game, to_territory_id)
        
    @staticmethod
    def army_vantage(game, territory_id):
        own_armies = game.board.armies(territory_id)
        htl_armies = sum([arm for tid, pid, arm in game.board.hostile_neighbors(territory_id)])
        return float(own_armies) / (htl_armies+0.01)        
 
    @classmethod
    def army_vantage_ratio(cls, game, from_territory_id, to_territory_id):
        return cls.army_vantage(game, from_territory_id) / \
               cls.army_vantage(game, to_territory_id)
    
    def fortify(self, game):
            possible_fortifications = game.board.possible_fortifications(self.player_id)
            if len(possible_fortifications) == 0:
                return None
            fort = max(possible_fortifications, key=lambda x: self.army_vantage_ratio(game, x[0], x[2]))
            return fort[0], fort[2], fort[1]-1
    
class PlacingPlayer (FortifyingPlayer):
    
    def place(self, game):
        options = game.board.territories_of(self.player_id)
        if isinstance(self.mission(game), missions.TerritoryMission) and len(options) >= 18:
            options = [o for o in options if game.board.armies(o) < 2]
            if len(options) == 0: # in this case the player has in principle won, but the turn needs to be completed to win
                options = game.board.territories_of(self.player_id)
        return min(options, key=lambda x: self.territory_vantage(game, x))