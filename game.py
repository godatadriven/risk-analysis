import copy
import random

import definitions
import missions
import board

class Game (object):
    
    def __init__(self, board, cards, missions, players, turn):
        self.board    = board
        self.cards    = cards
        self.missions = missions
        self.players  = players
        self.turn     = turn
       
    @classmethod
    def create(cls, players):
        n_players = len(players)
        return cls(
            board    = board.Board.create(n_players),
            cards    = cls.assign_cards(n_players),
            missions = cls.assign_missions(n_players),
            players  = cls.prepare_players(players),
            turn     = -1
        )
    
    @staticmethod
    def assign_cards(n_players):
        """ Assign reinforcement card placeholders to players. """
        return [[0, 0, 0] for pid in range(n_players)]
    
    @staticmethod
    def assign_missions(n_players):
        """ Assign missions to players. """
        available_missions = missions.missions(n_players)
        random.shuffle(available_missions)
        selected_missions = available_missions[:n_players]
        for pid, m in enumerate(selected_missions):
            m.assign_to(pid)
        return selected_missions
    
    @staticmethod
    def prepare_players(players):
        retval = [copy.deepcopy(p) for p in players]
        for pid, player in enumerate(retval):
            player.player_id = pid
        return retval
    
    def initialize_armies(self):
        """ Have all players place all starting armies on the board. """
        while self.initialize_single_army():
            continue
        self.next_turn()
            
    def initialize_single_army(self):
        """ Have each player place one army on the board, if they have one left. """
        changed = False
        for player in self.players:
            if self.board.n_armies(player.player_id) < self.starting_armies:
                territory = player.place(self)
                self.board.add_armies(territory, 1)
                changed = True
        return changed
    
    
    @property
    def current_player_id(self):
        """ Return the player id of the current turn. """
        return self.turn % self.n_players if self.turn >= 0 else None
 
    @property
    def current_player(self):
        return self.players[self.current_player_id] if self.current_player_id is not None else None

 
    
    @property
    def n_players(self):
        return len(self.players)
   
    def next_turn(self):
        self.turn += 1
        if not self.is_alive(self.current_player_id):
            self.next_turn()
            
    def has_ended(self):
        return self.winner() is not None

    def has_won(self, player_id):
        return self.is_alive(player_id) and self.missions[player_id].evaluate(self.board)
    
    def is_alive(self, player_id):
        return self.board.n_territories(player_id) > 0

    def attack(self, player):
        did_win = False
        while True:
            attack = player.attack(self)
            if attack is None:
                break
            # check valid owner
            if self.board.attack(*attack):
                did_win = True
        if did_win:
            self.give_card(player.player_id)
        
    def fortify(self, player):
        fortification = player.fortify(self)
        if fortification is not None:
            assert self.current_player_id == self.board.owner(fortification[0]), \
                'Game: invalid fortification: player move armies of another player'
            self.board.fortify(*fortification)


        
    def place(self, player):
        n_reinforcements = self.board.reinforcements(player.player_id)
        for i in range(n_reinforcements):
            territory_id = player.place(self)
            self.board.add_armies(territory_id, 1)   
        n_extra = self.use_cards(player.player_id, player.use_cards(self))
        for i in range(n_extra):
            territory_id = player.place(self)
            self.board.add_armies(territory_id, 1)        

    def play_turn(self):
        player = self.current_player
        assert self.is_alive(player.player_id), 'Player cannot perform a turn, he is game-over!'
        self.place(player)
        self.attack(player)
        self.fortify(player)
        self.next_turn()

    def give_card(self, player_id):
        card_type = random.randint(0,2)
        self.cards = [
            [(c+1 if ct == card_type else c) for ct, c in enumerate(cards)]
            if pid == player_id else cards
            for pid, cards in enumerate(self.cards)
        ]
        
    def card_options(self, player_id):
        cards = self.cards[player_id]
        infantry    = cards[0] >= 3
        cavalry     = cards[1] >= 3
        artillery   = cards[2] >= 3
        combination = min(cards) >= 1
        obligatory  = sum(cards) >= 5
        return ((infantry, cavalry, artillery, combination), obligatory)
    
    def use_cards(self, player_id, combination_id):
        cards = self.cards[player_id]
        if combination_id == 0: # infantry, 4 armies
            cards[0] -= 3
            retval = 4
        elif combination_id == 1: # cavalry, 6 armies
            cards[1] -= 3
            retval = 6
        elif combination_id == 2: # artillery, 8 armies
            cards[2] -= 3
            retval = 8
        elif combination_id == 3: # combination, 10 armies
            for i in range(3):
                cards[i] -= 1
            retval = 10
        else:
            return 0
        assert min(cards) >= 0, 'Player is cheating: handing in cards he does not own!'
        return retval
        
    @property
    def player_ids(self):
        return range(len(self.players))
    
    @property
    def starting_armies(self):
        return definitions.starting_armies[self.n_players]
    
    def winner(self):
        for player_id in self.player_ids:
            if self.has_won(player_id):
                return player_id
        return None
    