import json
import random

import pandas as pd

from ranker import RiskRanker


class PlayerPool(object):
    """
    The PlayerPool handles the running of the Risk GA.

    Args:
        player_cls (class): The player type to create.
        genes (iterable): Iterable containing dictionaries of genes for initializing players. If the length of this
            iterable is smaller than the pool size, additional players will be randomly initialized up to the pool
            size. Defaults to an empty iterable.
        max_turns (int): Maximum number of turns per game. Defaults to 1500.
        n_players (int): Number of players in a game. Defaults to 4.
        pool_size (int): Size of the gene pool. Defaults to 150.
        ranking_iterations (int): Number of games to play to create a rank. Defaults to 12.
    """

    def __init__(self, player_cls, genes=tuple(),
                 max_turns=1500, n_players=4, pool_size=150, ranking_iterations=12):
        self.iteration_counter = 0
        self.max_turns = max_turns
        self.n_players = n_players
        self.pool_size = pool_size
        self.ranking_iterations = ranking_iterations
        self.pool = self.initialize_players(player_cls, pool_size, genes)
        self.log = [self.gene_df]

    @property
    def genes(self):
        """
        Get all gene data.

        Returns:
            list: List of all genes currently in the pool.
        """
        return [p.genes for p in self.pool]

    @classmethod
    def load(cls, player_cls, filename, **kwargs):
        """
        Load a gene pool from a file.

        Args:
            player_cls (class): The player type to load into.
            filename (str): Path to the gene file.
            **kwargs: Additional arguments to pass the to PlayerPool.

        Returns:
            PlayerPool: Pool with loaded genes.
        """
        with open(filename, 'r') as sfile:
            genes = json.load(sfile)
        return cls(player_cls, genes=genes, **kwargs)

    def save(self, filename):
        """
        Save the gene pool to a file.

        Args:
            filename (str): Path to the gene file.
        """
        with open(filename, 'w') as sfile:
            json.dump(self.genes, sfile)

    def save_log(self, filename):
        """
        Save a log of all genes to a CSV file.

        Args:
            filename (str): Path to the log file.
        """
        pd.concat(self.log).to_csv(filename)

    @staticmethod
    def initialize_players(player_cls, pool_size, genes=tuple()):
        """
        Initialize players from gene data.

        Args:
            player_cls (class): Player class to initialize.
            pool_size (int): Number of players to initialize.
            genes (iterable): Iterable of gene dictionaries. Defaults to empty tuple.

        Returns:
            Initialized player objects.
        """
        retval = [player_cls(g) for g in genes]
        retval += [player_cls.create() for _ in range(pool_size - len(retval))]
        return retval

    def iteration(self):
        """
        Perform a single iteration.
        """
        self.iteration_counter += 1
        self.rank()
        good_players = self.pool[:self.pool_size / 4]
        comb_players = [random.choice(self.pool).combine(random.choice(self.pool)) for _ in range(self.pool_size / 4)]
        muta_players = [p.mutate() for p in random.sample(self.pool, self.pool_size / 2)]
        self.pool = good_players + comb_players + muta_players
        self.log.append(self.gene_df)

    @property
    def gene_df(self):
        """
        Create a pandas dataframe containing the current gene pool.

        Returns:
            pandas.DataFrame
        """
        df = pd.DataFrame([p.genes for p in self.pool])
        df['iteration'] = self.iteration_counter
        return df

    def rank(self):
        """
        Rank the players in the pool using a RiskRanker.
        """
        r = RiskRanker(self.pool, n_players=self.n_players, max_turns=self.max_turns)
        r.run(self.ranking_iterations)
        self.pool = r.ranked_players()
