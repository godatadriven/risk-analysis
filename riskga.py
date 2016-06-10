import game, ranker
import random
import pandas as pd

class RiskGA (object):
    
    def __init__(self, player_cls,
                 max_turns=1500, n_players=4, pool_size=150, ranking_iterations=12):
        self.max_turns = max_turns
        self.n_players = n_players
        self.pool_size = pool_size
        self.ranking_iterations = ranking_iterations
        self.pool = self.initialize_players(player_cls, pool_size)
        self.rank()
    
    @staticmethod
    def initialize_players(player_cls, pool_size):
        return [player_cls.create() for i in range(pool_size)]
    
    def iteration(self):
        good_players = self.pool[:self.pool_size/4]
        comb_players = [random.choice(self.pool).combine(random.choice(self.pool)) for i in range(self.pool_size/4)]
        muta_players = [p.mutate() for p in random.sample(self.pool, self.pool_size/2)]
        self.pool = good_players + comb_players + muta_players
        self.rank()
    
    @property
    def gene_df(self):
        return pd.DataFrame([p.genes for p in self.pool])
    
    def rank(self):
        r = ranker.RiskRanker(self.pool, n_players=self.n_players, max_turns=self.max_turns)
        r.run(self.ranking_iterations)
        self.pool = r.ranked_players()
        