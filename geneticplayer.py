from missions import TerritoryMission
from genome import Gene, ListGene, Genome
from player import SmartPlayer


class GeneticPlayer(SmartPlayer, Genome):
    """
    The GeneticPlayer decides which moves to make based on weights given to each move.


    """
    specifications = (
        # Turning in cards
        ListGene('turn_in_cutoff', values=[4, 6, 8, 10], volatility=0.01),

        # Attack weights
        Gene('att_bonus_wgt', min_value=-25., max_value=25., volatility=0.03, granularity=0.10, precision=2),
        Gene('att_chance_wgt', min_value=-25., max_value=25., volatility=0.03, granularity=0.10, precision=2),
        Gene('att_conqc_wgt', min_value=-25., max_value=25., volatility=0.03, granularity=0.10, precision=2),
        Gene('att_narmies_wgt', min_value=-25., max_value=25., volatility=0.03, granularity=0.10, precision=2),
        ListGene('att_mission_wgt', values=[-1, 0, 1], volatility=0.03),
        Gene('att_cutoff', min_value=-25., max_value=25., volatility=0.03, granularity=0.25, precision=1),
        Gene('att_cutoff_win', min_value=-25., max_value=25., volatility=0.015, granularity=0.25, precision=1),

        # Mission weights
        Gene('mis_base_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.25, precision=2),
        Gene('mis_cont_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.25, precision=2),
        Gene('mis_extr_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.25, precision=2),
        Gene('mis_terr_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.25, precision=2),
        ListGene('mis_play_wgt', values=[0, 1], volatility=0.01),

        # Reinforcement weights
        Gene('re_dbonus_wgt', min_value=-25., max_value=25., volatility=0.02, granularity=0.10, precision=2),
        Gene('re_ibonus_wgt', min_value=-25., max_value=25., volatility=0.02, granularity=0.10, precision=2),
        ListGene('re_mission_wgt', values=[-1, 0, 1], volatility=0.01),
        Gene('re_avantage_wgt', min_value=-25., max_value=25., volatility=0.02, granularity=0.10, precision=2),
        Gene('re_tvantage_wgt', min_value=-25., max_value=25., volatility=0.02, granularity=0.10, precision=2),

        # Fortification weights
        Gene('ft_min_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.10, precision=2),
        Gene('ft_avantage_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.10, precision=2),
        Gene('ft_tvantage_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.10, precision=2),
        Gene('ft_mission_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.10, precision=2),
        Gene('ft_bonus_wgt', min_value=-25., max_value=25., volatility=0.01, granularity=0.10, precision=2),
        ListGene('ft_narmies_wgt', values=[-1, 0, 1], volatility=0.005)
    )

    def turn_in_cards(self):
        """
         Decide whether or not to turn in cards, if possible. This is done based on the number of armies that
         the player would receive. If the number of armies is at least equal to the 'turn_in_cutoff' weight,
         the player turns them in.

         Returns:
             str/None: Name of set to turn in, or None.
         """
        complete_sets = {set_name: armies for set_name, armies in self.cards.complete_sets}
        if len(complete_sets) == 0:
            return None
        best_set, armies = max(complete_sets.items(), key=lambda x: x[1])
        if self.cards.obligatory_turn_in or armies >= self['turn_in_cutoff']:
            return best_set
        return None

    def attack(self, won_yet):
        """
        Decide which attack to make, if any.

        Args:
            won_yet (bool): True if player has won a territory yet in this turn.

        Returns:
            tuple/None: Tuple of the form (from_territory_id, to_territory_id, num_armies).
        """
        possible_attacks = self.attacks
        if len(possible_attacks) == 0:
            return None
        attack = max(possible_attacks, key=lambda x: self.attack_weight(x))
        if self.attack_weight(attack) < self.min_attack_weight(won_yet):
            return None
        return attack.from_territory_id, attack.to_territory_id, attack.from_armies - 1

    def attack_weight(self, attack):
        """
        Calculate the attack weight for an attack.

        Args:
            attack (Move): The attack.

        Returns:
            float: The weight of the attack.
        """
        return sum((
            self.direct_bonus(attack.to_territory_id) * self['att_bonus_wgt'],
            self.chance_ratio(attack) * self['att_chance_wgt'],
            self.conquering_chance(attack) * self['att_conqc_wgt'],
            self.mission_value(attack.to_territory_id) * self['att_mission_wgt'],
            (attack.from_armies - 1) * self['att_narmies_wgt'],
        ))

    def min_attack_weight(self, won_yet):
        """
        Calculate the minimum attack weight an attack needs before we attack.

        Args:
            won_yet (bool): True if the player has conquered a territory this turn.

        Returns:
            float: The minimum attack weight.
        """
        return self['att_cutoff'] + (self['att_cutoff_win'] if not won_yet else 0.)

    def fortify(self):
        """
        Decide which fortify move to make, if any.

        Returns:
            tuple/None: Tuple of the form (from_territory_id, to_territory_id, num_armies).
        """
        possible_fortifications = self.fortifications
        if len(possible_fortifications) == 0:
            return None
        fortification = max(possible_fortifications, key=lambda x: self.fortification_weight(x))
        if self.fortification_weight(fortification) < self['ft_min_wgt']:
            return None
        return fortification.from_territory_id, fortification.to_territory_id, fortification.from_armies - 1

    def fortification_weight(self, fortification):
        return sum((
            (self.army_vantage_difference(fortification)) * self['ft_avantage_wgt'],
            (self.territory_vantage_difference(fortification)) * self['ft_tvantage_wgt'],
            (self.mission_value(fortification.from_territory_id)
             - self.mission_value(fortification.to_territory_id)) * self['ft_mission_wgt'],
            (self.direct_bonus(fortification.from_territory_id)
             - self.direct_bonus(fortification.to_territory_id)) * self['ft_bonus_wgt'],
            (fortification.from_armies - 1) * self['ft_narmies_wgt']
        ))

    def reinforce(self):
        """
        Decide where to place an army.

        Returns:
            int: Territory ID.
        """
        options = self.territories
        if isinstance(self.mission, TerritoryMission) and len(options) >= 18:
            options = [o for o in options if self.board.armies(o) < 2]
            if len(options) == 0:  # in this case the player has in principle won, and only needs to finish his turn
                options = self.territories
        return max(options, key=lambda tid: self.reinforce_weight(tid))

    def reinforce_weight(self, territory_id):
        return sum((
            self.direct_bonus(territory_id) * self['re_dbonus_wgt'],
            self.continent_value(territory_id) * self['re_ibonus_wgt'],
            self.mission_value(territory_id) * self['re_mission_wgt'],
            self.army_vantage(territory_id) * self['re_avantage_wgt'],
            self.territory_vantage(territory_id) * self['re_tvantage_wgt']
        ))
