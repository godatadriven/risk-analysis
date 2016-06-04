import datetime,copy, math, random
import pandas as pd
import matplotlib.pyplot as plt
import game, missions

class RiskTester (object):
    
    def __init__(self, players, n_players=4):
        self.log           = [ ]
        self.players       = players
        self.n_players     = n_players
        self.prepare()
        
    def prepare(self):
        assert len(set(p.name for p in self.players)) == len(self.players), \
            'PlayerTester: requires players with unique names'
        self.player_games = {p.name: 0 for p in self.players}
        self.player_wins  = {p.name: 0 for p in self.players}
     
    @property
    def beliefs(self):
        return {name: self.belief(name) for name in self.player_names}

    @property
    def df(self):
        return pd.DataFrame(self.log)    
    
    @property
    def player_names(self):
        return set(p.name for p in self.players)
    
    def belief(self, player_name):
        wins = self.player_wins[player_name]
        if wins == 0:
            return {'score': 0., 'uncertainty': 1.}
        fact = 1./self.player_games[player_name]
        return {'score': wins*fact, 'uncertainty': math.sqrt(wins)*fact}
    

    

    
    def run(self, n_games=100):
        for i in range(n_games):
            players = self.random_select_players()
            self.play_game(players)
    
    def play_game(self, players):
        p = [copy.deepcopy(p) for p in players]
        start = datetime.datetime.now()
        g = game.Game.create(p)
        g.initialize_armies()
        while not g.has_ended():
            g.play_turn()
        end = datetime.datetime.now()
        self.log.append({
            'turn'           : g.turn,
            'n_players'      : len(players),
            'players'        : [p.name for p in players],
            'missions'       : [m.description for m in g.missions],
            'time'           : (end-start).total_seconds(),
            'winning_pid'    : g.winner().player_id,
            'winning_player' : g.winner().name,
            'winning_mission': g.winner().mission.description
        })
        self.update_scores([p.name for p in players], g.winner().name)
 
    def random_select_players(self):
        return [random.choice(self.players) for i in range(self.n_players)]

    def update_scores(self, player_names, winning_player_name):
        for player_name in player_names:
            self.player_games[player_name] += 1
        self.player_wins[winning_player_name] += self.n_players

    def plot_beliefs(self):
        scores, labels = [ ], [ ] 
        for key, item in self.beliefs.items():
            labels.append(key)
            score, err = item['score'], item['uncertainty']
            scores.append((score, score+2*err, max(0, score-2*err)))
        plt.boxplot(scores, showbox=True, labels=labels)
    
    
    def plot_player_stats(self, df=None):
        self.create_boxplot(self.count_wins_by_player(self.df if df is None else df))
        
    def plot_mission_stats(self, df=None):
        print df
        self.create_boxplot(self.count_wins_by_mission(self.df if df is None else df))
    
    def count_wins_by_player(self, df=None):
        if df is None:
            df = self.df
        raw_data = (
            (
                player,
                self.statistics(
                    sum(len([p for p in player_list if player == p]) for player_list in df['players']),
                    sum(df['winning_player'] == player)
                )
            ) for
            player in self.player_names
        )
        return self.create_count_df(raw_data)

    def count_wins_by_mission(self, df=None):
        if df is None:
            df = self.df
        raw_data = (
            (
                mission,
                self.statistics(
                    len(df[[(mission in mission_list) for mission_list in df['missions']]]),
                    len(df[df['winning_mission'] == mission])
                )
            ) for
            mission in sorted(df['winning_mission'].unique())
        )
        return self.create_count_df(raw_data)    
    
    @staticmethod
    def create_count_df(it):
        return pd.DataFrame([
            {
                'index': index,
                'mean' : mean,
                'se'   : se
            } for
            index, (mean, se) in it
        ]).set_index('index')
    
    @staticmethod
    def create_boxplot(df):
        plt.boxplot(
            zip(df['mean'], df['mean'] - df['se'], df['mean'] + df['se']),
            labels = df.index
        )
        plt.xticks(rotation=90)
        plt.show()
    
    @staticmethod
    def statistics(total, pos):
        """ Calculate the mean and the standard error on a set of boolean results which
            contains `total` samples, of which `pos` are positive. """
        if total == 0: return 0., 0.
        neg = total - pos
        mean = float(pos)/total
        stddev = math.sqrt((mean**2 * neg + (1.-mean)**2 * pos)/total)
        return mean, stddev / (math.sqrt(total))
