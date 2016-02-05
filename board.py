import pandas as pd
import random
import uuid
from definitions import *

class Board (object):
    def __init__(self, df=None, game_id=None, n_players=4):
        self.df = self._create_df(game_id, n_players) if df is None else df

        
    def _create_df(self, game_id=None, n_players=4):
        game_id = str(uuid.uuid1()) if game_id is None else game_id
        return pd.DataFrame({
            'event_type' : ['region']*42,
            'game_id'    : [game_id]*42,
            'turn'       : [0]*42,
            'region'     : range(42),
            'owner'      : self._create_random_allocation(n_players),
            'armies'     : [0]*42
        }).append(pd.DataFrame({
            'event_type' : ['card']*n_players,
            'turn'       : [0]*n_players,
            'game_id'    : [game_id]*n_players,
            'owner'      : range(n_players),
            'inf_card'   : [0]*n_players,
            'cav_card'   : [0]*n_players,
            'can_card'   : [0]*n_players,
        }))
    
    def _create_random_allocation(self, n_players):
        x = (range(n_players)*42)[0:42]
        random.shuffle(x)
        return x
    
    def n_players(self):
        return df['owner'].nunique()
    
    @property
    def state(self):
        return self.df.drop('game_id', axis=1)