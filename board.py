import definitions
import os
import random
import matplotlib.pyplot as plt


class Board(object):
    """
    The Board object keeps track of all armies situated on the Risk
    world map. Through the definitions it knows the locations of and
    connections between all territories. It handles ownership, attacks
    and movements of armies.

    Args:
        data (list): a sorted list of tuples describing the state of the
            board, each containing three values:
            - tid (int): the territory id of a territory,
            - pid (int): the player id of the owner of the territory,
            - n_armies (int): the number of armies on the territory.
            The list is sorted by the tid, and should be complete.
    """

    def __init__(self, data):
        self.data = data

    @classmethod
    def create(cls, n_players):
        """
        Create a Board and randomly allocate the territories. Place one army on each territory.
        
        Args:
            n_players (int): Number of players.
                
        Returns:
            Board: A board with territories randomly allocated to the players.
        """
        allocation = (range(n_players) * 42)[0:42]
        random.shuffle(allocation)
        return cls([(tid, pid, 1) for tid, pid in enumerate(allocation)])

    # ====================== #
    # == Neighbor Methods == #
    # ====================== #   

    def neighbors(self, territory_id):
        """
        Create a generator of all territories neighboring a given territory.
            
        Args:
            territory_id (int): ID of the territory to find neighbors of.

        Returns:
            generator: Generator of tuples of the form (territory_id, player_id, armies).
        """
        neighbor_ids = definitions.territory_neighbors[territory_id]
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if tid in neighbor_ids)

    def hostile_neighbors(self, territory_id):
        """
        Create a generator of all territories neighboring a given territory, of which
        the owner is not the same as the owner of the original territory.
            
        Args:
            territory_id (int): ID of the territory.
                
        Returns:
            generator: Generator of tuples of the form (territory_id, player_id, armies).
        """
        player_id = self.owner(territory_id)
        neighbor_ids = definitions.territory_neighbors[territory_id]
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid != player_id and tid in neighbor_ids))

    def friendly_neighbors(self, territory_id):
        """
        Create a generator of all territories neighboring a given territory, of which
        the owner is the same as the owner of the original territory.

        Args:
            territory_id (int): ID of the territory.

        Returns:
            generator: Generator of tuples of the form (territory_id, player_id, armies).
        """
        player_id = self.owner(territory_id)
        neighbor_ids = definitions.territory_neighbors[territory_id]
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid == player_id and tid in neighbor_ids))

    # ======================= #
    # == Continent Methods == #
    # ======================= #

    def continent(self, continent_id):
        """
        Create a generator of all territories that belong to a given continent.
            
        Args:
            continent_id (int): ID of the continent.

        Returns:
            generator: Generator of tuples of the form (territory_id, player_id, armies).
        """
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if
                tid in definitions.continent_territories[continent_id])

    def n_continents(self, player_id):
        """
        Calculate the total number of continents owned by a player.
        
        Args:
            player_id (int): ID of the player.
                
        Returns:
            int: Number of continents owned by the player.
        """
        return len([continent_id for continent_id in range(6) if self.owns_continent(player_id, continent_id)])

    def owns_continent(self, player_id, continent_id):
        """
        Check if a player owns a continent.
        
        Args:
            player_id (int): ID of the player.
            continent_id (int): ID of the continent.
            
        Returns:
            bool: True if the player owns all of the continent's territories.
        """
        return all((pid == player_id for (tid, pid, arm) in self.continent(continent_id)))

    def continent_owner(self, continent_id):
        """
        Find the owner of all territories in a continent. If the continent
        is owned by various players, return None.
            
        Args:
            continent_id (int): ID of the continent.
                
        Returns:
            int/None: Player_id if a player owns all territories, else None.
        """
        pids = set([pid for (tid, pid, arm) in self.continent(continent_id)])
        if len(pids) == 1:
            return pids.pop()
        return None

    def continent_fraction(self, continent_id, player_id):
        """
        Compute the fraction of a continent a player owns.
        
        Args:
            continent_id (int): ID of the continent.
            player_id (int): ID of the player.

        Returns:
            float: The fraction of the continent owned by the player.
        """
        c_data = list(self.continent(continent_id))
        p_data = [(tid, pid, arm) for (tid, pid, arm) in c_data if pid == player_id]
        return float(len(p_data)) / len(c_data)

    def num_foreign_continent_territories(self, continent_id, player_id):
        """
        Compute the number of territories owned by other players on a given continent.
        
        Args:
            continent_id (int): ID of the continent.
            player_id (int): ID of the player.

        Returns:
            int: The number of territories on the continent owned by other players.
        """
        return sum(1 if pid != player_id else 0
                   for (tid, pid, arm)
                   in self.continent(continent_id))

    # ==================== #
    # == Action Methods == #
    # ==================== #    

    def reinforcements(self, player_id):
        """
        Calculate the number of reinforcements a player is entitled to.
            
        Args:
            player_id (int): ID of the player.

        Returns:
            int: Number of reinforcement armies that the player is entitled to.
        """
        base_reinforcements = max(3, int(self.n_territories(player_id) / 3))
        bonus_reinforcements = 0
        for continent_id, bonus in definitions.continent_bonuses.items():
            if self.continent_owner(continent_id) == player_id:
                bonus_reinforcements += bonus
        return base_reinforcements + bonus_reinforcements

    def possible_attacks(self, player_id):
        """
        Assemble a list of all possible attacks for the players.

        Args:
            player_id (int): ID of the attacking player.

        Returns:
            list: each entry is an attack in the form of a tuple:
                (from_territory_id, from_armies, to_territory_id, to_player_id, to_armies).
        """
        return [(fr_tid, fr_arm, to_tid, to_pid, to_arm) for
                (fr_tid, fr_pid, fr_arm) in self.mobile(player_id) for
                (to_tid, to_pid, to_arm) in self.hostile_neighbors(fr_tid)]

    def possible_fortifications(self, player_id):
        """
        Assemble a list of all possible fortifications for the players.
        
        Args:
            player_id (int): ID of the attacking player.

        Returns:
            list: each entry is an attack in the form of a tuple:
                (from_territory_id, from_armies, to_territory_id, to_player_id, to_armies).
        """
        return [(fr_tid, fr_arm, to_tid, to_pid, to_arm) for
                (fr_tid, fr_pid, fr_arm) in self.mobile(player_id) for
                (to_tid, to_pid, to_arm) in self.friendly_neighbors(fr_tid)]

    def fortify(self, from_territory, to_territory, n_armies):
        """
        Perform a fortification.

        Args:
            from_territory (int): Territory_id of the territory where armies leave.
            to_territory (int): Territory_id of the territory where armies arrive.
            n_armies (int): Number of armies to move.

        Raises:
            ValueError if the player moves too many or negative armies.
            ValueError if the territories do not share a border or are not owned by the same player.
        """
        if n_armies < 0 or self.armies(from_territory) <= n_armies:
            raise ValueError('Board: Cannot move {n} armies from territory {tid}.'
                             .format(n=n_armies, tid=from_territory))
        if to_territory not in [tid for (tid, _, _) in self.friendly_neighbors(from_territory)]:
            raise ValueError('Board: Cannot fortify, territories do not share owner and/or border.')
        self.add_armies(from_territory, -n_armies)
        self.add_armies(to_territory, +n_armies)

    def attack(self, from_territory, to_territory, attackers):
        """
        Perform an attack.

        Args:
            from_territory (int): Territory_id of the offensive territory.
            to_territory (int): Territory_id of the defensive territory.
            attackers (int): Number of attacking armies.

        Raises:
            ValueError if the number of armies is <1 or too large.
            ValueError if a player attacks himself or the territories do not share a border.

        Returns:
            bool: True if the defensive territory was conquered, False otherwise.
        """
        if attackers < 1 or self.armies(from_territory) <= attackers:
            raise ValueError('Board: Cannot attack with {n} armies from territory {tid}.'
                             .format(n=attackers, tid=from_territory))
        if to_territory not in [tid for (tid, _, _) in self.hostile_neighbors(from_territory)]:
            raise ValueError('Board: Cannot attack, territories do not share border or are owned by the same player.')
        defenders = self.armies(to_territory)
        def_wins, att_wins = self.fight(attackers, defenders)
        if self.armies(to_territory) == att_wins:
            self.add_armies(from_territory, -attackers)
            self.set_armies(to_territory, attackers - def_wins)
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
        plt.figure(figsize=(16, 24))
        _ = plt.imshow(im)
        for territory, owner, armies in self.data:
            self.plot_single(territory, owner, armies)
        plt.axis('off')

    @staticmethod
    def plot_single(territory_id, player_id, armies):
        """
        Plot a single army dot.
            
        Args:
            territory_id (int): the id of the territory to plot,
            player_id (int): the player id of the owner,
            armies (int): the number of armies.
        """
        coor = definitions.territory_locations[territory_id]
        plt.scatter([coor[0]], [coor[1]], s=1250, c=definitions.player_colors[player_id])
        plt.text(coor[0], coor[1] + 25, s=str(armies),
                 color='black' if definitions.player_colors[player_id] in ['yellow', 'pink'] else 'white',
                 ha='center', size=30)

    # ==================== #
    # == Combat Methods == #
    # ==================== #    

    @classmethod
    def fight(cls, attackers, defenders):
        """
        Stage a fight.

        Args:
            attackers (int): Number of attackers.
            defenders (int): Number of defenders.

        Returns:
            tuple (int, int): Number of lost attackers, number of lost defenders.
        """
        n_attack_dices = min(attackers, 3)
        n_defend_dices = min(defenders, 2)
        attack_dices = sorted([cls.throw_dice() for _ in range(n_attack_dices)], reverse=True)
        defend_dices = sorted([cls.throw_dice() for _ in range(n_defend_dices)], reverse=True)
        wins = [att_d > def_d for att_d, def_d in zip(attack_dices, defend_dices)]
        return len([w for w in wins if w is False]), len([w for w in wins if w is True])

    @staticmethod
    def throw_dice():
        """
        Throw a dice.
        
        Returns:
            int: random int in [1, 6]. """
        return random.randint(1, 6)

    # ======================= #
    # == Territory Methods == #
    # ======================= #

    def owner(self, territory_id):
        """
        Get the owner of the territory.

        Args:
            territory_id (int): ID of the territory.

        Returns:
            int: Player_id that owns the territory.
        """
        return self.data[territory_id][1]

    def armies(self, territory_id):
        """
        Get the number of armies on the territory.

        Args:
            territory_id (int): ID of the territory.

        Returns:
            int: Number of armies in the territory.
        """
        return self.data[territory_id][2]

    def set_owner(self, territory_id, player_id):
        """
        Set the owner of the territory.

        Args:
            territory_id (int): ID of the territory.
            player_id (int): ID of the player.
        """
        self.data[territory_id] = (territory_id, player_id, self.armies(territory_id))

    def set_armies(self, territory_id, n):
        """
        Set the number of armies on the territory.

        Args:
            territory_id (int): ID of the territory.
            n (int): Number of armies on the territory.

        Raises:
            ValueError if n < 1.
        """
        if n < 1:
            raise ValueError('Board: cannot set the number of armies to <1 ({tid}, {n}).'.format(tid=territory_id, n=n))
        self.data[territory_id] = (territory_id, self.owner(territory_id), n)

    def add_armies(self, territory_id, n):
        """
        Add (or remove) armies to/from the territory.

        Args:
            territory_id (int): ID of the territory.
            n (int): Number of armies to add to the territory.

        Raises:
            ValueError if the resulting number of armies is <1.
        """
        self.set_armies(territory_id, self.armies(territory_id) + n)

    def n_armies(self, player_id):
        """
        Count the total number of armies owned by a player.

        Args:
            player_id (int): ID of the player.

        Returns:
            int: Number of armies owned by the player.
        """
        return sum((arm for tid, pid, arm in self.data if pid == player_id))

    def n_territories(self, player_id):
        """
        Count the total number of territories owned by a player.

        Args:
            player_id (int): ID of the player.

        Returns:
            int: Number of territories owned by the player.
        """
        return len([pid for tid, pid, arm in self.data if pid == player_id])

    def territories_of(self, player_id):
        """
        Return a set of all territories owned by the player.

        Args:
            player_id (int): ID of the player.

        Returns:
            list: List of all territory IDs owner by the player.
        """
        return [tid for (tid, pid, arm) in self.data if pid == player_id]

    def mobile(self, player_id):
        """
        Create a generator of all territories of a player which can attack or move,
        i.e. that have more than one army.

        Args:
            player_id (int): ID of the attacking player.

        Returns:
            generator: Generator of tuples of the form (territory_id, player_id, armies).
        """
        return ((tid, pid, arm) for (tid, pid, arm) in self.data if (pid == player_id and arm > 1))
