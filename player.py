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
        return definitions.player_colors[self.player_id]        
        
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

    def army_vantage_ratio(self, fr_tid, fr_arm, to_tid, to_pid, to_arm):
        return self.army_vantage(fr_tid) - self.army_vantage(to_tid)    
    
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
    
    def army_vantage(self, territory_id):
        """ Returns the ratio of hostile armies surrounding a territory
            to the friendly armies on the territory.
            
            Returns:
                float: army vantage [0, 1> """
        own_armies = self.board.armies(territory_id)
        htl_armies = sum(arm for tid, pid, arm in self.board.hostile_neighbors(territory_id))
        return float(htl_armies) / (htl_armies + own_armies)
    
    def territory_vantage(self, territory_id):
        """ Calculates the fraction of neighboring territories
            that are hostile.
            
            Returns:
                float: fraction of neighbors that are hostily [0, 1]. """
        htl_nb = len(list(self.board.hostile_neighbors(territory_id)))
        own_nb = len(list(self.board.friendly_neighbors(territory_id)))
        return float(htl_nb) / (htl_nb + own_nb)
    
    def direct_bonus(self, territory_id):
        """ Returns the direct bonus value of a territory, which is the continent bonus
            if the territory is the only territory of the continent not yet owned by
            the player, or the player owns the whole territory, normalised.
            
            Args:
                territory_id (int): territory ID for which to calculate the indirect bonus.
                
            Returns:
                float [0, 1]: the direct bonus. """
        continent_id = definitions.territory_continents[territory_id]
        num_foreign_territories = self.board.num_foreign_continent_territories(continent_id, self.player_id)
        if num_foreign_territories == 0 and self.board.owner(territory_id) == self.player_id:
            return definitions.continent_bonuses[continent_id] / 7.
        elif num_foreign_territories == 1 and self.board.owner(territory_id) != self.player_id:
            return definitions.continent_bonuses[continent_id] / 7.
        return 0.
    
    def indirect_bonus(self, territory_id):
        """ Returns the bonus value of a territory, which is defined as
               <fraction of continent player owns> * <continent bonus>, 
            normalised such that the result lies in [0, 1].
            
            Args:
                territory_id (int): territory ID for which to calculate the indirect bonus.
                
            Returns:
                float [0, 1]: the indirect bonus. """
        continent_id = definitions.territory_continents[territory_id]
        return self.board.continent_fraction(continent_id, self.player_id) * definitions.continent_bonuses[continent_id] / 7.
    
    @classmethod
    def chance_ratio(cls, fr_tid, fr_arm, to_tid, to_pid, to_arm):
        """ Calculate the ratio of the chances to lose armies to
            inflicting damage to foreign armies. This only depends
            on the number of dices.
            
            Returns:
                float: chance ratio, where lower is better [0.5, 3]. """
        return cls.chances[min(to_arm-1, 1)][min(fr_arm-2, 2)]
    
    @staticmethod
    def conquering_chance(fr_tid, fr_arm, to_tid, to_pid, to_arm):
        """ This function provides an estimate of the probability to
            conquer a territory based on the number of attacking and
            defending armies. This estimate is accurate at the 1% level. 
            
            Returns: 
                float: chance of conquering the territory [0, 1]. """
        n_att = fr_arm - 1.
        n_def = to_arm
        if n_att < 1: return 0.
        if n_att > n_def:
            return (n_att * 1.5) / (n_att + n_def)
        else:
            return (n_att * 1.25) / (n_att + n_def)
    
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
    
    def attack(self, won_yet):
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
    
    def attack(self, won_yet):
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
    
class GeneticPlayer (Player, genome.Genome, BasicFortifyMixin):
    
    specifications = (
        {'name': 'turn_in_cutoff', 'dtype': list, 'values': [4, 6, 8, 10], 'volatility': 0.01},
        
        {'name': 'att_bonus_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.03, 'granularity': 0.10, 'digits': 2},
        {'name': 'att_chance_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.03, 'granularity': 0.10, 'digits': 2},
        {'name': 'att_conqc_wgt', 'dtype': float, 'min_value': -25., 'max_value': 25.,
         'volatility': 0.03, 'granularity': 0.10, 'digits': 2},
        {'name': 'att_narmies_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.03, 'granularity': 0.10, 'digits': 2},
        {'name': 'att_mission_wgt', 'dtype': list, 'values': [-1, 0, 1], 'volatility': 0.01},
        {'name': 'att_cutoff', 'dtype': float, 'min_value': -10, 'max_value': +10,
         'volatility': 0.03, 'granularity': 0.25, 'digits': 1},
        {'name': 'att_cutoff_win', 'dtype': float, 'min_value': -10, 'max_value': +10,
         'volatility': 0.015, 'granularity': 0.25, 'digits': 1},
        
        {'name': 'mis_base_wgt', 'dtype': float, 'min_value': -5, 'max_value': +5,
         'volatility': 0.01, 'granularity': 0.25, 'digits': 2},
        {'name': 'mis_cont_wgt', 'dtype': float, 'min_value': -5, 'max_value': +5,
         'volatility': 0.01, 'granularity': 0.25, 'digits': 2},
        {'name': 'mis_extr_wgt', 'dtype': float, 'min_value': -5, 'max_value': +5,
         'volatility': 0.01, 'granularity': 0.25, 'digits': 2},
        {'name': 'mis_terr_wgt', 'dtype': float, 'min_value': -5, 'max_value': +5,
         'volatility': 0.01, 'granularity': 0.25, 'digits': 2},        
        {'name': 'mis_play_wgt', 'dtype': list, 'values': [-1, 0, 1], 'volatility': 0.005},
        
        {'name': 're_dbonus_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.02, 'granularity': 0.10, 'digits': 2},
        {'name': 're_ibonus_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.02, 'granularity': 0.10, 'digits': 2},
        {'name': 're_mission_wgt', 'dtype': list, 'values': [-1, 0, 1], 'volatility': 0.01},
        {'name': 're_avantage_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.02, 'granularity': 0.10, 'digits': 2},
        {'name': 're_tvantage_wgt', 'dtype': float, 'min_value': -15., 'max_value': 15.,
         'volatility': 0.02, 'granularity': 0.10, 'digits': 2},   
        
        {'name': 'ft_min_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.01, 'granularity': 0.10, 'digits': 2},   
        {'name': 'ft_avantage_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.01, 'granularity': 0.10, 'digits': 2},
        {'name': 'ft_tvantage_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.01, 'granularity': 0.10, 'digits': 2},   
        {'name': 'ft_mission_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.01, 'granularity': 0.10, 'digits': 2},   
        {'name': 'ft_bonus_wgt', 'dtype': float, 'min_value': -10., 'max_value': 10.,
         'volatility': 0.01, 'granularity': 0.10, 'digits': 2},
        {'name': 'ft_narmies_wgt', 'dtype': list, 'values': [-1, 0, 1], 'volatility': 0.005},


    )
    
    def mission_value(self, territory_id):
        if isinstance(self.mission, missions.PlayerMission):
            if self.mission.target_id == self.player_id:
                return self['mis_base_wgt'] if (self.board.n_territories(self.player_id) < 24) else 0.
            else:
                return self['mis_play_wgt'] if (self.board.owner(territory_id) == self.mission.target_id) else 0.
        elif isinstance(self.mission, missions.ContinentMission):
            continent_id = definitions.territory_continents[territory_id]
            if continent_id in self.mission.continents:
                return self['mis_cont_wgt']
            elif isinstance(self.mission, missions.ExtraContinentMission):
                if not any(self.board.owns_continent(self.player_id, cid) for cid in self.mission.other_continents):
                    return self['mis_extr_wgt'] * self.board.continent_fraction(continent_id, self.player_id)
            return 0.
        elif isinstance(self.mission, missions.BaseMission):
            return self['mis_base_wgt'] if (self.board.n_territories(self.player_id) < 24) else 0.
        elif isinstance(self.mission, missions.TerritoryMission):
            return self['mis_terr_wgt'] if (self.board.n_territories(self.player_id) < 18) else 0.
        else:
            raise Exception('Player: unknown mission: {m}'.format(m=self.mission))    

    def turn_in_cards(self):
        complete_sets = {sn: arm for sn, arm in self.cards.complete_sets}
        if len(complete_sets) == 0: return None
        best_set, armies = max(complete_sets.items(), key=lambda x: x[1])
        if self.cards.obligatory_turn_in:
            return best_set
        if armies >= self['turn_in_cutoff']:
            return best_set
        return None      

    def attack(self, won_yet):
        possible_attacks = self.possible_attacks()
        if len(possible_attacks) == 0: return None
        attack = max(possible_attacks,
                     key=lambda x: self.attack_weight(*x))
        if self.attack_weight(*attack) < self.min_attack_weight(won_yet): return None
        fr_tid, fr_arm, to_tid, to_pid, to_arm = attack
        return fr_tid, to_tid, fr_arm-1     
    
    def attack_weight(self, *attack):
        fr_tid, fr_arm, to_tid, to_pid, to_arm = attack
        return sum((
            self.direct_bonus(to_tid) * self['att_bonus_wgt'],
            self.chance_ratio(*attack) * self['att_chance_wgt'],
            self.conquering_chance(*attack) * self['att_conqc_wgt'],
            self.mission_value(to_tid) * self['att_mission_wgt'],
            (fr_arm - 1) * self['att_narmies_wgt'],
        ))
                                          
    def min_attack_weight(self, won_yet):
        return self['att_cutoff'] + (self['att_cutoff_win'] if not won_yet else 0.)

    def fortify(self):
        possible_fortifications = self.possible_fortifications()
        if len(possible_fortifications) == 0: return None
        fortification = max(possible_fortifications,
                            key=lambda x: self.fortification_weight(*x))
        if self.fortification_weight(*fortification) < self['ft_min_wgt']: return None
        fr_tid, fr_arm, to_tid, to_pid, to_arm = fortification
        return fr_tid, to_tid, fr_arm-1      
    
    def fortification_weight(self, fr_tid, fr_arm, to_tid, to_pid, to_arm):
        return sum((
                (self.army_vantage(fr_tid) - self.army_vantage(to_tid)) * self['ft_avantage_wgt'],
                (self.territory_vantage(fr_tid) - self.territory_vantage(to_tid)) * self['ft_tvantage_wgt'],
                (self.mission_value(fr_tid) - self.mission_value(to_tid)) * self['ft_mission_wgt'],
                (self.direct_bonus(fr_tid) - self.direct_bonus(to_tid)) * self['ft_bonus_wgt'],
                (fr_arm - 1) * self['ft_narmies_wgt']
        ))
    
    def reinforce(self):
        options = self.my_territories()
        if isinstance(self.mission, missions.TerritoryMission) and len(options) >= 18:
            options = [o for o in options if self.board.armies(o) < 2]
            if len(options) == 0: # in this case the player has in principle won, but the turn needs to be completed to win
                options = self.my_territories()
        return max(options, key=lambda tid: self.reinforce_weight(tid))
    
    def reinforce_weight(self, territory_id):
        return sum((self.direct_bonus(territory_id) * self['re_dbonus_wgt'],
                    self.indirect_bonus(territory_id) * self['re_ibonus_wgt'],
                    self.mission_value(territory_id) * self['re_mission_wgt'],
                    self.army_vantage(territory_id) * self['re_avantage_wgt'],
                    self.territory_vantage(territory_id) * self['re_tvantage_wgt']))
            
            
            
            
            
        