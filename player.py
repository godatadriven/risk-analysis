import copy, random
import definitions

class Player (object):
    """ The Player class is the basic player object. By itself, a Player
        cannot play the game. For this, it needs to be combined with Mixins
        which implement the `reinforce()`, `turn_in_cards()`, `attack()` and
        `fortify()` methods.
        
        The Player has internal references to the board on which it is playing,
        to the cards it has, and to its mission. Additionally, it has methods
        which calculate certain quantities based on these game objects. """
    
    def __init__(self, name=None):
        self.name      = name
        
    def __repr__(self):
        return '{dscr}({name})'.format(dscr=self.description, name=self.name)

    def copy(self):
        return copy.deepcopy(self)
    
    def join(self, player_id, board, cards, mission):
        self.player_id = player_id
        self.board     = board
        self.cards     = cards
        self.mission   = mission

    @property
    def color(self):
        return definitions.player_color[self.player_id]        
        
    @property
    def description(self):
        return self.__class__.__name__        

    def my_territories(self):
        return self.board.territories_of(self.player_id)
        
    def possible_attacks(self):
        return self.board.possible_attacks(self.player_id)
        
    def possible_fortifications(self):
        return self.board.possible_fortifications(self.player_id)
    
    # ==================== #
    # == Metric methods == #
    # ==================== #

    @staticmethod
    def army_ratio(fr_tid, fr_arm, to_tid, to_pid, to_arm):
        return float(fr_arm-1) / to_arm
    
    def army_vantage(self, territory_id):
        own_armies = self.board.armies(territory_id)
        htl_armies = sum([arm for tid, pid, arm in self.board.hostile_neighbors(territory_id)])
        return float(own_armies) / (htl_armies+0.01)
    
    def territory_vantage(self, territory_id):
        hn_count = len(list(self.board.hostile_neighbors(territory_id)))
        fn_count = len(list(self.board.friendly_neighbors(territory_id)))
        return float(fn_count) / (0.01 + hn_count)

    def army_vantage_ratio(self, fr_tid, fr_arm, to_tid, to_pid, to_arm):
        return self.army_vantage(fr_tid) / self.army_vantage(to_tid)    
    
    # ======================= #
    # == Exception methods == #
    # ======================= #    
    
    pass

    
class RandomReinforceMixin (object):
    
    def reinforce(self):
        return random.choice(self.my_territories())
    
    def turn_in_cards(self):
        complete_sets = [sn for sn, arm in self.cards.complete_sets]
        if len(complete_sets) == 0 or (not self.cards.obligatory_turn_in and random.random() > 0.5):
            return None
        return random.choice(complete_sets)
    
class RandomAttackMixin (object):
    
    def attack(self):
        if random.random() > 0.90 and self.board.n_armies(self.player_id) < 50:
            return None
        possible_attacks = self.possible_attacks()
        if len(possible_attacks) == 0:
            return None
        fr_tid, fr_arm, to_tid, to_pid, to_arm = random.choice(possible_attacks)
        return fr_tid, to_tid, fr_arm-1

class RandomFortifyMixin (object):
    
    def fortify(self):
        possible_fortifications = self.possible_fortifications()
        if len(possible_fortifications) == 0:
            return None
        fr_tid, fr_arm, to_tid, to_pid, to_arm = random.choice(possible_fortifications)
        return fr_tid, to_tid, random.randint(1, fr_arm-1)

class RuleBasedCardsBase (object):
    
    def turn_in_cards(self):
        complete_sets = {sn: arm for sn, arm in self.cards.complete_sets}
        if self.cards.obligatory_turn_in:
            return max(complete_sets.items(), key=lambda x: x[1])[0]
        if 'mix' in complete_sets:
            return 'mix'
        return None     
    
class BasicReinforceMixin (RuleBasedCardsBase):
    
    def reinforce(self):
        options = self.my_territories()
        if isinstance(self.mission, missions.TerritoryMission) and len(options) >= 18:
            options = [o for o in options if game.board.armies(o) < 2]
            if len(options) == 0: # in this case the player has in principle won, but the turn needs to be completed to win
                options = game.board.territories_of(self.player_id)
        return min(options, key=lambda x: self.territory_vantage(x))

class BasicAttackMixin (object):
    
    def attack(self):
        possible_attacks = self.possible_attacks()
        if len(possible_attacks) == 0: return None
        attack = max(possible_attacks,
                     key=lambda x: self.army_ratio(*x))
        if self.army_ratio(*attack) < 1: return None
        fr_tid, fr_arm, to_tid, to_pid, to_arm = attack
        return fr_tid, to_tid, fr_arm-1 

class BasicFortifyMixin (object):
    
    def fortify(self):
        possible_fortifications = self.possible_fortifications()
        if len(possible_fortifications) == 0:
            return None
        fortification = max(possible_fortifications,
                            key=lambda x: self.army_vantage_ratio(*x))
        fr_tid, fr_arm, to_tid, to_pid, to_arm = fortification
        return fr_tid, to_tid, fr_arm-1     
    
class RandomPlayer (Player, RandomReinforceMixin, RandomAttackMixin, RandomFortifyMixin):
    pass

class BasicPlayer (Player, BasicReinforceMixin, BasicAttackMixin, BasicFortifyMixin):
    pass
