import random

import definitions

class Player (object):
    
    def __init__(self, name=None):
        self.name      = name
        self.player_id = None
    
    @property
    def color(self):
        return definitions.player_color[self.player_id]
    
    def attack(self, b):
        raise Exception('base player cannot play')
    def fortify(self, b):
        raise Exception('base player cannot play')
    def place(self, b):
        raise Exception('base player cannot play')        

class RandomPlayer (Player):
    
    def attack(self, game):
        if random.random() > 0.75 and game.board.n_armies(self.player_id) < 50:
            return None
        possible_attacks = game.board.possible_attacks(self.player_id)
        if len(possible_attacks) == 0:
            return None
        attack = random.choice(possible_attacks)
        return attack[0], attack[2], attack[1]-1

    def fortify(self, game):
        possible_fortifications = game.board.possible_fortifications(self.player_id)
        if len(possible_fortifications) == 0:
            return None
        fortification = random.choice(possible_fortifications)
        return fortification[0], fortification[2], random.randint(1, fortification[1]-1)

    def init(self, game):
        return random.choice(list(game.board.territories_of(self.player_id)))

    def place(self, game, n):
        return [self.init(game) for x in range(n)]