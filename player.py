import copy, random
import definitions, missions

class Player (object):
    chances = [[1.41, 0.73, 0.52], [2.89, 1.57, 0.85]]
    
    """ The Player class is the basic player object. By itself, a Player
        cannot play the game. For this, it needs to be combined with Mixins
        which implement the `reinforce()`, `turn_in_cards()`, `attack()` and
        `fortify()` methods.
        
        The Player has internal references to the board on which it is playing,
        to the cards it has, and to its mission. Additionally, it has methods
        which calculate certain quantities based on these game objects. """
        

    def copy(self):
        raise Exception("Copying player!")
        return copy.deepcopy(self)
    
    def join(self, player_id, board, cards, mission):
        self.player_id = player_id
        self.board     = board
        self.cards     = cards
        self.mission   = mission
        
    def clear(self):
        del self.player_id
        del self.board
        del self.cards
        del self.mission

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
    
    def mission_value(self, territory_id):
        if isinstance(self.mission, missions.PlayerMission):
            if self.mission.target_id == self.player_id:
                return self.board.n_territories(self.player_id) < 24
            else:
                return 1. if self.board.owner(territory_id) == self.mission.target_id else 0.
        elif isinstance(self.mission, missions.ContinentMission):
            continent_id = definitions.territory_continents[territory_id]
            if continent_id in self.mission.continents:
                return 1.
            if isinstance(self.mission, missions.ExtraContinentMission):
                if any(self.board.owns_continent(self.player_id, cid) for cid in self.mission.other_continents):
                    return 0.
                else:
                    return self.board.continent_fraction(continent_id, self.player_id)
            else:
                return 0.
        elif isinstance(self.mission, missions.BaseMission):
            return self.board.n_territories(self.player_id) < 24
        elif isinstance(self.mission, missions.TerritoryMission):
            return self.board.n_territories(self.player_id) < 18
        else:
            raise Exception('Player: unknown mission: {m}'.format(m=self.mission))
                            
    def continent_value(self, territory_id):
        continent_id = definitions.territory_continents[territory_id]
        return self.board.continent_fraction(continent_id, self.player_id) * definitions.continent_bonuses[continent_id] 
    
    @classmethod
    def probability(cls, fr_tid, fr_arm, to_tid, to_pid, to_arm):
        return cls.chances[min(to_arm-1, 1)][min(fr_arm-2, 2)]
    
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
            options = [o for o in options if self.board.armies(o) < 2]
            if len(options) == 0: # in this case the player has in principle won, but the turn needs to be completed to win
                options = self.my_territories()
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

class SmartReinforceMixin (RuleBasedCardsBase):
    
    def territory_weight(self, territory_id):
        vantage         = -self.territory_vantage(territory_id)
        mission_value   = self.mission_value(territory_id)
        continent_value = self.continent_value(territory_id)
        return (vantage + mission_value + continent_value/5.) - 2.
    
    def reinforce(self):
        options = self.my_territories()
        if isinstance(self.mission, missions.TerritoryMission) and len(options) >= 18:
            options = [o for o in options if self.board.armies(o) < 2]
            if len(options) == 0: # in this case the player has in principle won, but the turn needs to be completed to win
                options = self.my_territories()
        return max(options, key=lambda tid: self.territory_weight(tid))

class RandomPlayer (Player, RandomReinforceMixin, RandomAttackMixin, RandomFortifyMixin):
    pass

class BasicPlayer (Player, BasicReinforceMixin, BasicAttackMixin, BasicFortifyMixin):
    pass

class SmartPlayer (Player, SmartReinforceMixin, BasicAttackMixin, BasicFortifyMixin):
    pass
    
import genome    
    
class GeneticPlayer (Player, genome.Genome, BasicAttackMixin, BasicFortifyMixin):
    
    specifications = (
        {'name': 'vantage_wgt', 'dtype': float, 'min_value': -1., 'max_value': 1., 
         'volatility': 0.25, 'granularity': 0.15, 'digits': 2},
        {'name': 'mission_wgt', 'dtype': float, 'min_value': -1., 'max_value': 1., 
         'volatility': 0.25, 'granularity': 0.15, 'digits': 2},
        {'name': 'continent_wgt', 'dtype': float, 'min_value': -1., 'max_value': 1., 
         'volatility': 0.25, 'granularity': 0.15, 'digits': 2},
        {'name': 'turn_in_cutoff', 'dtype': list, 'values': [4, 6, 8, 10], 'volatility': 0.05},
        {'name': 'att_prob_wgt', 'dtype': float, 'min_value': -2., 'max_value': 2.,
         'volatility': 0.10, 'granularity': 0.15, 'digits': 2},
        {'name': 'att_mis_wgt', 'dtype': list, 'values': [-1, 0, 1], 'volatility': 0.10},
        {'name': 'min_att_wgt', 'dtype': float, 'min_value': -5, 'max_value': +5,
         'volatility': 0.10, 'granularity': 0.25, 'digits': 1}
    )

    def turn_in_cards(self):
        complete_sets = {sn: arm for sn, arm in self.cards.complete_sets}
        if len(complete_sets) == 0: return None
        best_set, armies = max(complete_sets.items(), key=lambda x: x[1])
        if self.cards.obligatory_turn_in:
            return best_set
        if armies >= self['turn_in_cutoff']:
            return best_set
        return None      

    def attack(self):
        possible_attacks = self.possible_attacks()
        if len(possible_attacks) == 0: return None
        attack = max(possible_attacks,
                     key=lambda x: self.attack_weight(*x))
        if self.attack_weight(*attack) < self['min_att_wgt']: return None
        fr_tid, fr_arm, to_tid, to_pid, to_arm = attack
        return fr_tid, to_tid, fr_arm-1     
    
    def attack_weight(self, *attack):
        probability_value = self.probability(*attack)
        mission_value      = self.mission_value(attack[2])
        return (probability_value * self['att_prob_wgt'] +
                mission_value * self['att_mis_wgt'])
    
    def territory_weight(self, territory_id):
        vantage         = -self.territory_vantage(territory_id)
        mission_value   = self.mission_value(territory_id)
        continent_value = self.continent_value(territory_id)
        return (vantage*self['vantage_wgt'] + mission_value*self['mission_wgt'] + continent_value*self['continent_wgt'])
    
    def reinforce(self):
        options = self.my_territories()
        if isinstance(self.mission, missions.TerritoryMission) and len(options) >= 18:
            options = [o for o in options if self.board.armies(o) < 2]
            if len(options) == 0: # in this case the player has in principle won, but the turn needs to be completed to win
                options = self.my_territories()
        return max(options, key=lambda tid: self.territory_weight(tid))