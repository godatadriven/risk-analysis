import itertools
import random
import game
from trueskill import TrueSkill


class TrueskillRanker (object):
    """
    The TrueskillRanker keeps handles the ranking of players.

    Args:
        **kwargs: Arguments to pass to TrueSkill object.
    """
    
    def __init__(self, **kwargs):
        self.ratings = {}
        self.ts = TrueSkill(**kwargs)

    def __getitem__(self, player_id):
        try:
            return self.ratings[player_id]
        except KeyError:
            return self.ts.create_rating()
        
    def update(self, winner_pids, loser_pids):
        """
        Update the scores of players.

        Args:
            winner_pids (iterable): Iterable of player IDs in the winning group.
            loser_pids (iterable): Iterable of player IDs in the losing group.
        """
        winner_ratings = [self[pid] for pid in winner_pids]
        loser_ratings = [self[pid] for pid in loser_pids]
        new_winner_ratings, new_loser_ratings = self.ts.rate([winner_ratings, loser_ratings], [0, 1])
        for pid, rating in zip(winner_pids, new_winner_ratings):
            self.ratings[pid] = rating
        for pid, rating in zip(loser_pids, new_loser_ratings):
            self.ratings[pid] = rating
    
    def rank(self):
        """
        Rank all known players.

        Returns:
            list: Ranked list of tuples (player_id, score), where the first is the best.
        """
        return sorted(((pid, self.score(pid)) for pid in self.ratings.keys()), key=lambda x: x[1], reverse=True)
        
    def score(self, player_id):
        """
        Returns the score (the exposed rating) of a player.

        Args:
            player_id: The ID of a player.

        Returns:
            float: The score of the player. Returns 0 if the player is not known.
        """
        return self.ts.expose(self[player_id])


class RiskRanker (TrueskillRanker):
    """
    The RiskRanker is a TrueskillRanker which handles the full process of ranking a set of players,
    including the playing of games. The player_id of a player is id(player).

    Args:
        players (iterable): Iterable of Player objects. These players will be ranked.
        n_players (int): Number of players in a game. Defaults to 4.
        max_turns (int): Maximum number of turns to play. This prevents dead situations. Defaults to 1500.
        **kwargs: Arguments to pass to TrueSkill.
    """
    
    def __init__(self, players, n_players=4, max_turns=1500, **kwargs):
        super(RiskRanker, self).__init__(**kwargs)
        self.players = {}
        self.initialize(players)
        self.n_players = n_players
        self.max_turns = max_turns
             
    def initialize(self, players):
        """
        Initialize player dictionary.

        Args:
            players (iterable): Iterable of Player objects.
        """
        self.players = {id(p): p for p in players}
        if not len(players) == len(self.players):
            raise ValueError('A player may only be passed once!')

    def iteration(self):
        """ Run a single iteration: i.e. have every player play at least one game. """
        for pool in self.player_pools():
            self.play_game(pool)
            
    def run(self, n):
        """
        Run n iterations.

        Args:
            n (int): Number of iterations to run.
        """
        for i in range(n):
            self.iteration()
            
    def ranked_players(self):
        """
        Rank the players.

        Returns:
            list: List of player objects. The first player is the best.
        """
        return [self.players[pid] for pid, _ in self.rank()]
                
    def play_game(self, player_ids):
        """
        Play a single game.

        Args:
            player_ids (list): List of player ids that will play.
        """
        players = [self.players[pid] for pid in player_ids]
        for pid in player_ids:
            if id(self.players[pid]) != pid:
                raise Exception('Player changed id!')
        g = game.Game.create(players)
        g.initialize_armies()
        for i in range(self.max_turns):
            g.play_turn()
            if g.has_ended():
                break
        if g.winner() is not None:
            winner_pid = id(g.winner())
            self.update([winner_pid], [pid for pid in player_ids if winner_pid != pid])
        for p in players:
            p.clear()
            
    @property
    def player_ids(self):
        return self.players.keys()
        
    def player_pools(self):
        """
        Randomly create player pool that will play against each other. The last pool will be filled up with random
        players, such that every player will be in at least one pool.

        Returns:
            list of lists: List of player pools, each represented by a list of player ids.
        """
        ids = self.player_ids
        random.shuffle(ids)
        while len(ids) % self.n_players > 0:
            ids.append(random.choice(list(set(ids)-set(ids[-self.n_players:]))))
        return itertools.izip(*[itertools.islice(ids, i, None, self.n_players) for i in range(self.n_players)])
