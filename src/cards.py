import random


class Cards(object):
    """
    The Cards object keeps track of the Risk cards of a single player.
    At the end of each turn a player receives a Risk card if he has
    conquered at least one territory during that turn. Risk cards come
    in three kinds: infantry, cavalry and artillery. At the beginning
    of a turn, a player may turn in a set of Risk cards to receive extra
    reinforcements, depending on the card set. There are four valid sets:
     - "infantry", consisting of 3 infantry cards, worth 4 armies,
     - "cavalry", consisting of 3 cavalry cards, worth 6 armies,
     - "artillery", consisting of 3 artillery cards, worth 8 armies,
     - "mix", consisting of 1 card of each kind, worth 10 armies.
    If a player holds 5 cards at the beginning of a turn, he _must_ turn
    in a set of cards.

    Args:
        n_inf (int): Number of infantry cards. Defaults to 0.
        n_cav (int): Number of cavalry cards. Defaults to 0.
        n_art (int): Number of artillery cards. Defaults to 0.
    """

    card_sets = {
        'infantry': ((3, 0, 0), 4),
        'cavalry': ((0, 3, 0), 6),
        'artillery': ((0, 0, 3), 8),
        'mix': ((1, 1, 1), 10)
    }

    def __init__(self, n_inf=0, n_cav=0, n_art=0):
        self.cards = [n_inf, n_cav, n_art]

    def __repr__(self):
        return '{cls}{cards}'.format(cls=self.__class__.__name__, cards=tuple(self.cards))

    @property
    def obligatory_turn_in(self):
        """
        A player is obliged to turn in reinforcement cards if he has 5.
        This property is True if this is the case.

        Returns:
            bool: True if the total number of cards is equal to a greater than 5.
        """
        return self.total_cards > 4

    @property
    def complete_sets(self):
        """
        Tuple of complete sets of cards that can be turned in.

        Returns:
            tuple: All sets that can be turned in, each represented by a tuple
                of the form (set_name (str), armies (int)).
        """
        return tuple(
            (set_name, armies) for
            set_name, (card_set, armies) in
            self.card_sets.items() if
            self.is_complete(set_name)
        )

    @property
    def total_cards(self):
        """
        Total number of cards in the hand.

        Returns:
            int: Total number of cards in the hand.
        """
        return sum(self.cards)

    def receive(self):
        """
        Receive a card. Randomly picks a card and adds it to the hand.

        Returns:
            None
        """
        card_type = random.randint(0, 2)
        self.cards[card_type] += 1

    def turn_in(self, set_name):
        """
        Turn in a complete set of cards.

        Args:
            set_name (str): Name of the card set.

        Raises:
            ValueError if the set is not complete.

        Returns:
            int: The number of reinforcements received.
        """
        card_set, armies = self.card_sets[set_name]
        if not self.is_complete(set_name):
            raise ValueError('{self}: cannot turn in {set_name}, it is incomplete!'
                             .format(self=self, set_name=set_name))
        for card_index, n_cards in enumerate(card_set):
            self.cards[card_index] -= n_cards
        return armies

    def is_complete(self, set_name):
        """
        Check if a card set is complete.

        Args:
            set_name (str): Name of the card set.

        Raises:
            KeyError if the set name is unknown.

        Returns:
            bool: True if the set is complete, False otherwise.
        """
        card_set, _ = self.card_sets[set_name]
        return all(oc >= sc for sc, oc in zip(card_set, self.cards))
