import random

class Cards (object):
    """ The Cards object keeps track of the Risk cards of a single player.
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
        in a set of cards. """
    
    card_sets = {
        'infantry' : ((3, 0, 0), 4),  
        'cavalry'  : ((0, 3, 0), 6), 
        'artillery': ((0, 0, 3), 8), 
        'mix'      : ((1, 1, 1), 10)
    }
    
    def __init__(self):
        """ Initializes an empty hands of cards. """
        self.cards = [0, 0, 0]
    
    def __repr__(self):
        return '{cls}{cards}'.format(cls=self.__class__.__name__, cards=tuple(self.cards))

    @property
    def obligatory_turn_in(self):
        """ If a player owns 5 cards he is obliged to turn in a set of cards.
            
            Returns:
                bool: which is true of the total number of cards is equal or greater than 5. """
        return self.total_cards >= 5
    
    @property
    def complete_sets(self):
        """ Constructs a tuple of sets that can be turned in.
        
            Returns:
                tuple: tuple of sets that can be turned in, each represented by a tuple
                    of the form (set_name, armies). """
        return tuple(
            (set_name, armies) for
            set_name, (card_set, armies) in 
            self.card_sets.items() if
            self.is_complete(card_set)
        )

    @property
    def total_cards(self):
        """ Calculates the total number of cards.
        
            Returns:
                int: the total number of cards. """
        return sum(self.cards)    
    
    def receive(self):
        """ Receive a card. """
        card_type = random.randint(0,2)
        self.cards[card_type] += 1
        
    def turn_in(self, set_name):
        """ Turn in a set of cards.
        
            Args:
                set_name (string): name of the card set.
                
            Returns:
                int: number of armies received. """
        card_set, armies = self.card_sets[set_name]
        if not self.is_complete(card_set):
            raise Exception('{self}: cannot turn in {set_name}, it is incomplete!' \
                            .format(self=self, set_name=set_name))
        for card_index, n_cards in enumerate(card_set):
            self.cards[card_index] -= n_cards
        return armies
                
    def is_complete(self, card_set):
        """ Check if a card set is held in hand.
        
            Args:
                card_set (tuple): tuple of three ints, describing 
                    the number of cards of each type required for the set.
                    
            Rerturns:
                bool: True if the set is complete, False otherwise. """
        return all(oc >= sc for sc, oc in zip(card_set, self.cards))