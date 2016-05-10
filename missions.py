import definitions

class Mission (object):
    
    def __init__(self):
        self.player_id = None
         
    def __repr__(self):
        return 'Mission(void)'
    
    def assign_to(self, player_id):
        """ Assign the mission to a player.
            
            Args:
                player_id (int): ID of the player to assign to. """
        self.player_id = player_id
    
    def evaluate(self, board):
        """ Evaluate whether the mission has been achieved.
        
            Args:
                board (Board): The board to evaluate.
                
            Returns:
                bool: returns True if the mission is achieved, False otherwise. """
        if self.player_id is None:
            raise Exception('Mission: cannot evaluate: not assigned to a player')
        return self._evaluate(board)
 
    def score(self, board):
        """ Calculate the fraction of the mission which is completed. This may
            be useful for AI to evaluate its next move.
        
            Args:
                board (Board): The board to evaluate.
                
            Returns:
                float: score between 0 and 1. """
        if self.player_id is None:
            raise Exception('Mission: cannot evaluate: not assigned to a player')
        return self._score(board)

    @property
    def double_occupancy(self):
        return False
    
    def _evaluate(self, board):
        raise Exception('Mission: base mission cannot be evaluated.')
        
    def _score(self, board):
        raise Exception('Mission: base mission cannot be scored.')

class BaseMission (Mission):
    
    def __repr__(self):
        return 'Mission("conquer at least 24 territories")'
    
    def _evaluate(self, board):
        return board.n_territories(self.player_id) >= 24
    
    def _score(self, board):
        return max(0., board.n_territories(self.player_id) / 24.)
        
class TerritoryMission (Mission):
        
    def __repr__(self):
        return 'Mission("conquer at least 18 territories and have at least 2 armies on each territory")'

    @property
    def double_occupancy(self):
        return True
    
    def _criterium(self, board):
        """ Return the number of territories owned by the player, with at least the minimum number of armies. """
        return len([tid for (tid, pid, arm) in board.data if (pid == self.player_id and arm >= 2)]) >= 18
    
    def _evaluate(self, board):
        """ The mission is succesful if the number of territories is equal or larger than the minimum. """
        return self._criterium(board) >= 18
    
    def _score(self, board):
        """ The score is the fraction of territories owned. """
        return self._criterium(board) / 18. 

class PlayerMission (BaseMission):
    
    def __init__(self, target_id):
        """ Initialize a PlayerMission.
        
            Args:
                target_id (int): ID of the player which needs to be eliminated."""
        super(PlayerMission, self).__init__()
        self.target_id = target_id
        
    def __repr__(self):
        if self.target_id == self.player_id:
            return 'Mission("fallback: conquer at least 24 territories")'
        else:
            return 'Mission("eliminate the {color} player")'.format(color=definitions.player_colors[self.target_id])
    
    def _evaluate(self, board):
        if self.target_id == self.player_id:
            return super(PlayerMission, self)._evaluate(board)
        else:
            return board.n_territories(self.target_id) == 0
    
    def _score(self, board):
        if self.target_id == self.player_id:
            return super(PlayerMission, self)._score(board)
        else:
            return (42 - (board.n_territories(self.target_id))) / 42.

class ContinentMission (Mission):
    
    def __init__(self, continents):
        """ Initialize a ContinentMission.
        
            Args:
                continents (list): List of continent_ids which are to be conquered. """
        super(ContinentMission, self).__init__()
        self.continents    = continents
        
    def __repr__(self):
        return 'Mission("conquer {continents}")'.format(
            continents=' and '.join([definitions.continent_names[cid] for cid in self.continents])
        )

    def _evaluate(self, board):
        for continent_id in self.continents:
            if board.continent_owner(continent_id) != self.player_id:
                return False
        return True
    
    def _score(self, board):
        return sum([
            board.continent_fraction(cid, self.player_id) for cid in self.continents
        ]) / len(self.continents)

class ExtraContinentMission (ContinentMission):
    
    def __repr__(self):
        return 'Mission("conquer {continents} and an additional continent of choice")'.format(
            continents=' and '.join([definitions.continent_names[cid] for cid in self.continents]))
    
    def _evaluate(self, board):
        for continent_id in self.continents:
            if board.continent_owner(continent_id) != self.player_id:
                return False
        return board.n_continents(self.player_id) > len(self.continents)

    @property
    def other_continents(self):
        return (cid for cid in range(6) if not cid in self.continents)
    
    def _score(self, board):
        base_score = sum((board.continent_fraction(cid, self.player_id) for cid in self.continents))
        add_score = max((board.continent_fraction(cid, self.player_id) for cid in self.other_continents))
        return float(base_score + add_score) / (len(self.continents) + 1)
    
def missions(n_players):
    """ Return all available missions for the given number of players.
    
        Args:
            n_players (int): Number of players in the game.
            
        Returns:
            list of Missions """
    base_missions = [
        ContinentMission((1, 5)),
        ContinentMission((0, 1)),
        ContinentMission((0, 3)),
        ContinentMission((3, 4)),
        ExtraContinentMission((2, 5)),
        ExtraContinentMission((2, 4)),
        BaseMission(),
        TerritoryMission()
    ]
    player_missions = [
        PlayerMission(pid) for pid in range(n_players)
    ]
    return base_missions + player_missions
