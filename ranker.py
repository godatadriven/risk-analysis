import itertools
import random
import game
import trueskill

class TrueskillRanker (object):
    
    def __init__(self, **kwargs):
        self.ratings = { }
        self.ts = trueskill.TrueSkill(**kwargs)
        
    def rating(self, pid):
        try:
            return self.ratings[pid]
        except KeyError:
            return self.ts.create_rating()
        
    def update(self, winner_pids, loser_pids):
        winner_ratings = [self.rating(pid) for pid in winner_pids]
        loser_ratings  = [self.rating(pid) for pid in loser_pids]
        new_winner_ratings, new_loser_ratings = self.ts.rate([winner_ratings, loser_ratings], [0, 1])
        for pid, rating in zip(winner_pids, new_winner_ratings):
            self.ratings[pid] = rating
        for pid, rating in zip(loser_pids, new_loser_ratings):
            self.ratings[pid] = rating
    
    def rank(self):
        return sorted(((pid, self.score(pid)) for pid in self.ratings.keys()), key=lambda x: x[1], reverse=True)
    
    def register(self, pid):
        self.ratings[pid] = self.ts.create_rating()
        
    def score(self, pid):
        return trueskill.expose(self.rating(pid))

class RiskRanker (TrueskillRanker):
    
    def __init__(self, players, n_players=4, max_turns=1500, **kwargs):
        super(RiskRanker, self).__init__(**kwargs)
        self.initialize(players)
        self.n_players = n_players
        self.max_turns = max_turns
             
    def initialize(self, players):
        self.players = {id(p): p for p in players}
        assert len(players) == len(self.players), 'Single player passed multiple times!'

    def iteration(self):
        for pool in self.player_pools():
            self.play_game(pool)
            
    def run(self, n):
        for i in range(n):
            self.iteration()
            
    def ranked_players(self):
        return [self.players[pid] for pid, score in self.rank()]
                
    def play_game(self, player_ids):
        players = [self.players[pid] for pid in player_ids]
        g = game.Game.create(players)
        g.initialize_armies()
        for i in range(self.max_turns):
            g.play_turn()
            if g.has_ended(): break
        winner_pid = id(g.winner())
        self.update([winner_pid], [pid for pid in player_ids if winner_pid != pid])
        for p in players:
            p.clear()
            
    @property
    def player_ids(self):
        return self.players.keys()
        
    def player_pools(self):
        ids = self.player_ids
        random.shuffle(ids)
        while len(ids) % self.n_players > 0:
            ids.append(random.choice(list(set(ids)-set(ids[-self.n_players:]))))
        return itertools.izip(*[itertools.islice(ids, i, None, self.n_players) for i in range(self.n_players)])
      