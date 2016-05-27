import definitions
import os
import random
import matplotlib.pyplot as plt


class Board (object):
    
    def __init__(self, data):
        self.data = data
    
    @classmethod
    def create(cls, n_players):
        """ Create a Board, randomly allocate the territoriess and place one army on each territory.
        
            Args:
                n_players (int): Number of players.
                
            Returns:
                Board: A board with territories randomly allocated for the players. """
        allocation = (range(n_players)*42)[0:42]
        random.shuffle(allocation)
        return cls([(tid, pid, 1) for tid, pid in enumerate(allocation)])
    
    def owner(self, territory_id):
        """ Get the owner of the territory. 
        
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                int, Player_id that owns the territory. """
        return self.data[territory_id][1]
    
    def armies(self, territory_id):
        """ Get the number of armies in the territory. 
        
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                int, Number of armies in the territory. """
        return self.data[territory_id][2]
    
    def set_owner(self, territory_id, player_id):
        """ Set the owner of the territory.
        
            Args:
                territory_id (int): ID of the territory.
                player_id (int): ID of the player. """
        self.data[territory_id] = (territory_id, player_id, self.armies(territory_id))
    
    def set_armies(self, territory_id, n):
        """ Set the number of armies in the territory.
            
            Args:
                territory_id (int): ID of the territory.
                n (int): Number of armies on the territory. """
        assert n > 0, 'Board: setting the number of armies on territory {r} to {n}!'.format(r=territory_id, n=n)
        self.data[territory_id] = (territory_id, self.owner(territory_id), n) 
        
    def add_armies(self, territory_id, n):
        """ Add (or remove) armies to/from the territory.
            
            Args:
                territory_id (int): ID of the territory.
                n (int): Number of armies to add to the territory. """
        self.set_armies(territory_id, self.armies(territory_id)+n)
        
    def n_armies(self, player_id):
        """ Calculate the total number of armies owned by a player.
        
            Args:
                player_id (int): ID of the player.
                
            Returns:
                int: Number of armies owned by the player. """
        return sum((arm for tid, pid, arm in self.data if pid == player_id))
        
    def n_territories(self, player_id):
        """ Calculate the total number of territories owned by a player.
        
            Args:
                player_id (int): ID of the player.
                
            Returns:
                int: number of territories owned by the player. """
        return len([pid for tid, pid, arm in self.data if pid == player_id])
    
    def n_continents(self, player_id):
        """ Calculate the total number of continents owned by a player.
        
            Args:
                player_id (int): ID of the player.
                
            Returns:
                int: Number of continents owned by the player. """
        return len([continent_id for continent_id in range(6) if self.continent_owner(continent_id) == player_id])
    
    def possible_attacks(self, player_id):
        """ Assemble a list of all possible attacks for the players.
        
            Args:
                player_id (int): ID of the attacking player.
                
            Returns:
                list: each entry is an attack in the form of a tuple:
                    (from_territory_id, from_armies, to_territory_id, to_player_id, to_armies). """
        return [(fr_tid, fr_arm, to_tid, to_pid, to_arm) for 
                    (fr_tid, fr_pid, fr_arm) in self.mobile(player_id) for
                    (to_tid, to_pid, to_arm) in self.hostile_neighbors(fr_tid)]  

    def possible_fortifications(self, player_id):
        """ Assemble a list of all possible fortifications for the players.
        
            Args:
                player_id (int): ID of the attacking player.
                
            Returns:
                list: each entry is an attack in the form of a tuple:
                    (from_territory_id, from_armies, to_territory_id, to_player_id, to_armies). """
        return [(fr_tid, fr_arm, to_tid, to_pid, to_arm) for 
                    (fr_tid, fr_pid, fr_arm) in self.mobile(player_id) for
                    (to_tid, to_pid, to_arm) in self.friendly_neighbors(fr_tid)]  
    
    def mobile(self, player_id):
        """ Create an iterator over all territories of a player which can attack or move,
            i.e. that have more than one army.
            
            Args:
                player_id (int): ID of the attacking player.
                
            Returns:
                list: list of tuples of the form (territory_id, player_id, armies). """           
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid == player_id and arm > 1))
    
    def neighbors(self, territory_id):
        """ Create an iterator over all territories neighboring a given territory.
            
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                list: list of tuples of the form (territory_id, player_id, armies). """ 
        neighbor_ids = definitions.territory_neighbors[territory_id]
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if tid in neighbor_ids)
    
    def hostile_neighbors(self, territory_id):
        """ Create an iterator over all territories neighboring a given territory, of which
            the owner is not the same as the owner of the original territory.
            
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                list: list of tuples of the form (territory_id, player_id, armies). """ 
        player_id    = self.owner(territory_id)
        neighbor_ids = definitions.territory_neighbors[territory_id]
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid != player_id and tid in neighbor_ids))
 
    def friendly_neighbors(self, territory_id):
        """ Create an iterator over all territories neighboring a given territory, of which
            the owner is the same as the owner of the original territory.
            
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                list: list of tuples of the form (territory_id, player_id, armies). """ 
        player_id    = self.owner(territory_id)
        neighbor_ids = definitions.territory_neighbors[territory_id]
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid == player_id and tid in neighbor_ids))

    def continent(self, continent_id):
        """ Create an iterator over all territories that belong to a given continent.
            
            Args:
                continent_id (int): ID of the continent.
                
            Returns:
                list: list of tuples of the form (territory_id, player_id, armies). """
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if tid in definitions.continent_territories[continent_id])  
    
    def continent_owner(self, continent_id):
        """ Find the owner of all territories in a continent. If the continent
            is owned by various players, return None.
            
            Args:
                continent_id (int): ID of the continent.
                
            Returns:
                int/None: player_id if any player owns all territories, else None. """
        pids = set([pid for (tid, pid, arm) in self.continent(continent_id)])
        if len(pids) == 1:
            return list(pids)[0]
        return None
    
    def continent_fraction(self, continent_id, player_id):
        c_data = list(self.continent(continent_id))
        p_data = [(tid, pid, arm) for (tid, pid, arm) in c_data if pid == player_id]
        return float(len(p_data)) / len(c_data)
    
    def reinforcements(self, player_id):
        """ Calculate the number of reinforcements a player is entitled to.
            
            Args:
                player_id (int): ID of the player.
                
            Returns:
                int: number of reinforcment armies that the player is entitled to. """
        base_reinforcements  = max(3, int(self.n_territories(player_id) / 3))
        bonus_reinforcements = 0
        for continent_id, bonus in definitions.continent_bonuses.items():
            if self.continent_owner(continent_id) == player_id:
                bonus_reinforcements += bonus
        return base_reinforcements + bonus_reinforcements

    def territories_of(self, player_id):
        """ Return a set of all territories owned by the player.
            
            Args:
                player_id (int): ID of the player.
                
            Returns:
                set: set of territory IDs """        
        return set((tid for (tid, pid, arm) in self.data if pid == player_id))

    def fortify(self, from_territory, to_territory, n_armies):
        assert self.armies(from_territory) > n_armies, \
            'Board: invalid fortification: too many armies.'
        assert n_armies >= 0, \
            'Board: invalid fortification: zero or negative number of armies moved.'
        assert self.owner(from_territory) == self.owner(to_territory), \
            'Board: invalid fortification: territories do not share the owner.'
        assert to_territory in definitions.territory_neighbors[from_territory], \
            'Board: invalid fortification: territories do not share border.'
        self.add_armies(from_territory, -n_armies)
        self.add_armies(to_territory, +n_armies)
        
    def attack(self, from_territory, to_territory, n_armies):
        assert self.armies(from_territory) > n_armies, \
            'Player is using more armies to attack than allowed!'
        attackers = n_armies
        defenders = self.armies(to_territory)
        att_wins, def_wins = fight(attackers, defenders)
        if self.armies(to_territory) == att_wins:
            self.add_armies(from_territory, -n_armies)
            self.set_armies(to_territory, n_armies - def_wins)
            self.set_owner(to_territory, self.owner(from_territory))
            return True
        else:
            self.add_armies(from_territory, -def_wins)
            self.add_armies(to_territory, -att_wins)
        return False
    
    def plot(self):
        im = plt.imread(os.getcwd() + '/risk.png')
        plt.figure(figsize=(10, 15))
        implot = plt.imshow(im)
        for territory, owner, armies in self.data:
            self.plot_single(territory, owner, armies)
        plt.show()
        
    def plot_single(self, territory, owner, armies):
        coor = definitions.territory_locations[territory]
        plt.scatter([coor[0]], [coor[1]], s = 300, c=definitions.player_colors[owner])
        plt.text(coor[0], coor[1]+12, s=str(armies), 
                 color='black' if definitions.player_colors[owner] == 'yellow' else 'white',
                 ha='center', size='x-large')    
    

def fight(attackers, defenders):
    n_attack_dices = min(attackers, 3)
    n_defend_dices = min(defenders, 2)
    attack_dices = sorted([throw_dice() for i in range(n_attack_dices)], reverse=True)
    defend_dices = sorted([throw_dice() for i in range(n_defend_dices)], reverse=True)
    wins = [att_d > def_d for att_d, def_d in zip(attack_dices, defend_dices)]
    return len([w for w in wins if w is True]), len([w for w in wins if w is False])   
    
def throw_dice():
    return random.randint(1, 6)  