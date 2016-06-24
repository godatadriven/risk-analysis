import definitions
import os, random
import matplotlib.pyplot as plt


class Board (object):
    """ The Board object keeps track of all armies situated on the Risk
        world map. Through the definitions it knows the locations of and
        connections between all territories. It handles ownership, attacks
        and movements of armies. """
    
    def __init__(self, data):
        """ Initialize a Board from the data. 
        
            Args:
                data (list): a sorted list of tuples describing the state of the 
                    board, each containing three values:
                    - tid (int): the territory id of a territory,
                    - pid (int): the player id of the owner of the territory,
                    - n_armies (int): the number of armies on the territory. 
                    The list is sorted by the tid, and should be complete. """
        self.data = data
    
    @classmethod
    def create(cls, n_players):
        """ Create a Board, randomly allocate the territories and place one army on each territory.
        
            Args:
                n_players (int): Number of players.
                
            Returns:
                Board: A board with territories randomly allocated for the players. """
        allocation = (range(n_players)*42)[0:42]
        random.shuffle(allocation)
        return cls([(tid, pid, 1) for tid, pid in enumerate(allocation)])

    # ======================= #
    # == Territory Methods == #
    # ======================= #     
    
    def owner(self, territory_id):
        """ Get the owner of the territory. 
        
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                int: Player_id that owns the territory. """
        return self.data[territory_id][1]
    
    def armies(self, territory_id):
        """ Get the number of armies in the territory. 
        
            Args:
                territory_id (int): ID of the territory.
                
            Returns:
                int: Number of armies in the territory. """
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
    
    def territories_of(self, player_id):
        """ Return a set of all territories owned by the player.
            
            Args:
                player_id (int): ID of the player.
                
            Returns:
                set: set of territory IDs """        
        return [tid for (tid, pid, arm) in self.data if pid == player_id] 
    
    def mobile(self, player_id):
        """ Create an iterator over all territories of a player which can attack or move,
            i.e. that have more than one army.
            
            Args:
                player_id (int): ID of the attacking player.
                
            Returns:
                list: list of tuples of the form (territory_id, player_id, armies). """           
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid == player_id and arm > 1))

    # ====================== #
    # == Neighbor Methods == #
    # ====================== #   
    
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

    # ======================= #
    # == Continent Methods == #
    # ======================= #
    
    def continent(self, continent_id):
        """ Create an iterator over all territories that belong to a given continent.
            
            Args:
                continent_id (int): ID of the continent.
                
            Returns:
                iterator: over tuples of the form (territory_id, player_id, armies). """
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if tid in definitions.continent_territories[continent_id])  

    def n_continents(self, player_id):
        """ Calculate the total number of continents owned by a player.
        
            Args:
                player_id (int): ID of the player.
                
            Returns:
                int: Number of continents owned by the player. """
        return len([continent_id for continent_id in range(6) if self.owns_continent(player_id, continent_id)])    
    
    def owns_continent(self, player_id, continent_id):
        """ Check if the player owns the continent.
        
            Args:
                player_id (int): ID of the player.
                continent_id (int): ID of the continent.
            
            Returns:
                bool: True if the player owns all of the continent's territories. """
        return all((pid == player_id for (tid, pid, arm) in self.continent(continent_id)))
    
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
        """ Compute which fraction of the continent the player owns.
        
            Args:
                continent_id (int): ID of the continent.
                player_id (int): ID of the player.
            
            Returns:
                float: The fraction of the continent owned by the player. """
        c_data = list(self.continent(continent_id))
        p_data = [(tid, pid, arm) for (tid, pid, arm) in c_data if pid == player_id]
        return float(len(p_data)) / len(c_data)
    
    def num_foreign_continent_territories(self, continent_id, player_id):
        """ Compute the number of territories on a continent owned by other players.
        
            Args:
                continent_id (int): ID of the continent.
                player_id (int): ID of the player.
            
            Returns:
                int: The number of territories on the continent owned by other player. """
        return sum(1 if pid != player_id else 0 
                   for (tid, pid, arm) 
                   in self.continent(continent_id))

    # ==================== #
    # == Action Methods == #
    # ==================== #    
    
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

    def fortify(self, from_territory, to_territory, n_armies):
        """ Perform a fortification.
        
            Args:
                from_territory (int): Territory_id of the territory where armies leave.
                to_territory (int): Territory_id of the territory where armies arrive.
                n_armies (int): Number of armies to move. """
        assert self.armies(from_territory) > n_armies, \
            'Board: invalid fortification: too many armies.'
        assert n_armies >= 0, \
            'Board: invalid fortification: negative number of armies moved.'
        assert self.owner(from_territory) == self.owner(to_territory), \
            'Board: invalid fortification: territories do not share owner.'
        assert to_territory in definitions.territory_neighbors[from_territory], \
            'Board: invalid fortification: territories do not share border.'
        self.add_armies(from_territory, -n_armies)
        self.add_armies(to_territory, +n_armies)
        
    def attack(self, from_territory, to_territory, n_armies):
        """ Perform an attack.
        
            Args:
                from_territory (int): Territory_id of the offensive territory.
                to_territory (int): Territory_id of the defensive territory.
                n_armies (int): Number of attacking armies.
                
            Returns:
                bool: True if the defensive territory was conquered, False otherwise. """
        assert self.armies(from_territory) > n_armies, \
            'Board: invalid attack: using more armies than allowed!'
        assert n_armies > 0, \
            'Board: invalid attack: no armies used.'
        assert self.owner(from_territory) != self.owner(to_territory), \
            'Board: invalid attack: player attacking his own land.'
        assert to_territory in definitions.territory_neighbors[from_territory], \
            'Board: invalid attack: territories do not share border.'
        attackers = n_armies
        defenders = self.armies(to_territory)
        def_wins, att_wins = self.fight(attackers, defenders)
        if self.armies(to_territory) == att_wins:
            self.add_armies(from_territory, -n_armies)
            self.set_armies(to_territory, n_armies - def_wins)
            self.set_owner(to_territory, self.owner(from_territory))
            return True
        else:
            self.add_armies(from_territory, -def_wins)
            self.add_armies(to_territory, -att_wins)
            return False

    # ====================== #
    # == Plotting Methods == #
    # ====================== #    
    
    def plot_board(self):
        """ Plot the board. """
        im = plt.imread(os.getcwd() + '/risk.png')
        plt.figure(figsize=(10, 15))
        implot = plt.imshow(im)
        for territory, owner, armies in self.data:
            self.plot_single(territory, owner, armies)
        
    def plot_single(self, territory_id, player_id, armies):
        """ Plot a single army dot.
            
            Args:
                territory_id (int): the id of the territory to plot,
                player_id (int): the player id of the owner,
                armies (int): the number of armies. """
        coor = definitions.territory_locations[territory_id]
        plt.scatter([coor[0]], [coor[1]], s = 300, c=definitions.player_colors[player_id])
        plt.text(coor[0], coor[1]+12, s=str(armies), 
                 color='black' if definitions.player_colors[player_id] in ['yellow', 'pink'] else 'white',
                 ha='center', size='x-large')    
    
    # ==================== #
    # == Combat Methods == #
    # ==================== #    
    
    @classmethod
    def fight(cls, attackers, defenders):
        """ Stage a fight.
        
            Args:
                attackers (int): Number of attackers.
                defenders (int): Number of defenders.
                
            Returns:
                tuple (int, int): Number of lost attackers, number of lost defenders. """
        n_attack_dices = min(attackers, 3)
        n_defend_dices = min(defenders, 2)
        attack_dices = sorted([cls.throw_dice() for i in range(n_attack_dices)], reverse=True)
        defend_dices = sorted([cls.throw_dice() for i in range(n_defend_dices)], reverse=True)
        wins = [att_d > def_d for att_d, def_d in zip(attack_dices, defend_dices)]
        return len([w for w in wins if w is False]), len([w for w in wins if w is True])   
    
    @staticmethod
    def throw_dice():
        """ Throw a dice.
        
            Returns:
                int: random int in [1, 6]. """
        return random.randint(1, 6)  