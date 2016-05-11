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
        return [(pid, 0, 0, 0) for pid in range(n_players)]
    
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
                territory = player.init(self)
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
        return self.missions[player_id].evaluate(self.board)
    
    def is_alive(self, player_id):
        return self.board.n_territories(player_id) > 0

    def attack(self, player):
        did_win = False
        while True:
            attack = player.attack(self)
            if attack is None:
                return
            # check valid owner
            if self.board.attack(*attack):
                did_win = True
        # give card to player
        
    def fortify(self, player):
        fortification = player.fortify(self)
        if fortification is not None:
            assert self.current_player_id == self.board.owner(fortification[0]), \
                'Game: invalid fortification: player move armies of another player'
            self.board.fortify(*fortification)


        
    def place(self, player):
        n_reinforcements = self.board.reinforcements(player.player_id)
        territories      = player.place(self, n_reinforcements)
        assert len(territories) == n_reinforcements, 'Player is cheating!'
        for tid in territories:
            self.board.add_armies(tid, 1)

    def play_turn(self):
        player = self.current_player
        assert self.is_alive(player.player_id), 'Player cannot perform a turn, he is game-over!'
        self.place(player)
        self.attack(player)
        self.fortify(player)
        self.next_turn()

      
        
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
    