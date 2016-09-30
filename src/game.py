import random

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import definitions
from board import Board
from cards import Cards
from missions import missions as get_missions


class Game(object):
    """
    The Game object handles all aspects of a Risk game. It contains one Board
    object and a Cards object for each player. The Game also contains a Player
    object for each player, which it asks for decisions during each game step.
    """

    def __init__(self, board, cards, missions, players, turn):
        """
        Initialize the Game.
        
        Args:
           board (Board): the game Board, initialized for the correct number of players.
           cards (list): list of Cards objects, one for each player.
           missions (list): list of Mission objects, one for each player.
           players (list): list of Player objects.
           turn (int): current turn number.
        """
        self.board = board
        self.cards = cards
        self.missions = missions
        self.players = players
        self.turn = turn
        self.assign_players()

    def assign_players(self):
        """
        Assign respective missions to players, and have each player join the game.
        """
        for pid, player in enumerate(self.players):
            player.join(self, pid)
            self.missions[pid].assign_to(pid)

    @classmethod
    def create(cls, players):
        """
        Create a new Game.
        
        Args:
            players (list): List of Players.
                
        Returns:
            Game: newly initialized Game object.
        """
        n_players = len(players)
        return cls(
            board=Board.create(n_players),
            cards=cls.assign_cards(n_players),
            missions=cls.assign_missions(n_players),
            players=players,
            turn=-1
        )

    @staticmethod
    def assign_cards(n_players):
        """
        Assign reinforcement card hands to players.

        Args:
            n_players (int): Number of players to assign cards to.

        Returns:
            list: List of Cards objects, one for each player.
        """
        return [Cards() for _ in range(n_players)]

    @staticmethod
    def assign_missions(n_players):
        """
        Randomly assign missions to players.

        Args:
            n_players (int): Number of players to assign missions to.

        Returns:
            list: List of missions, one for each player.
        """
        available_missions = get_missions(n_players)
        random.shuffle(available_missions)
        return available_missions[:n_players]

    def initialize_armies(self):
        """
        Have all players place all starting armies on the board.
        """
        while self.initialize_single_army():
            continue
        self.next_turn()

    def initialize_single_army(self):
        """
        Have each player place one army on the board, if they have one left.
        
        Returns:
            bool, True if at least one player has placed a new army. False if all armies have been placed.
        """
        changed = False
        for player in self.players:
            if self.board.n_armies(player.player_id) < self.starting_armies:
                territory_id = player.reinforce()
                self.board.add_armies(territory_id, 1)
                changed = True
        return changed

    @property
    def current_player_id(self):
        """
        Return the player id of the current turn.
        
        Returns:
            int/None: ID of the player whose turn it is, None if the game has not started yet.
        """
        return self.turn % self.n_players if self.turn >= 0 else None

    @property
    def current_player(self):
        """
        Return the player of the current turn.
        
        Returns:
            Player/None: Player whose turn it is, None if the game has not started yet.
        """
        return self.players[self.current_player_id] if self.current_player_id is not None else None

    @property
    def n_players(self):
        """
        Return the number of players in the game, including those that are game-over.
        
        Returns:
            int: The number of players.
        """
        return len(self.players)

    @property
    def player_ids(self):
        """
        Return all player ids in the game.
        
        Returns:
            generator: For all player ids in the game.
        """
        return range(len(self.players))

    @property
    def starting_armies(self):
        """
        Return the number of armies each player can place at the start.
        
        Returns:
            int: Total number of starting armies per player.
        """
        return definitions.starting_armies[self.n_players]

    def next_turn(self):
        """
        Jump to the next turn. Skip any dead players.
        """
        self.turn += 1
        if not self.is_alive(self.current_player_id):
            self.next_turn()

    def winner(self):
        """
        Return the winning player, if any.
        
        Returns:
            Player/None: the winning player, or None if there is none.
        """
        for player_id in self.player_ids:
            if self.has_won(player_id):
                return self.players[player_id]
        return None

    def has_ended(self):
        """
        Checks if the game has ended.
        
        Returns:
            bool: True if there is a winner, else False.
        """
        return self.winner() is not None

    def has_won(self, player_id):
        """
        Checks if a player has won.
        
        Args:
            player_id (int): The player id of the player to check.
                
        Returns:
            bool: True if the player has won, else False.
        """
        return self.is_alive(player_id) and (
            self.missions[player_id].evaluate(self.board) or
            self.board.n_territories(player_id) == 42
        )

    def is_alive(self, player_id):
        """
        Checks if a player is still alive.
        
        Args:
            player_id (int): The player id of the player to check.
                
        Returns:
            bool: True if the player has armies left, else False.
        """
        return self.board.n_territories(player_id) > 0

    # ================== #
    # == Turn methods == #
    # ================== #

    def play_turn(self):
        """
        Play a turn.
        The turn consists of three stages:
                - reinforcement,
                - attack,
                - fortification.
        """
        if not self.is_alive(self.current_player_id):
            raise Exception('Player cannot perform a turn, he is game-over!')
        self.reinforce(self.current_player)
        self.attack(self.current_player)
        self.fortify(self.current_player)
        self.next_turn()

    def reinforce(self, player):
        """
        Handle the reinforcement phase of a player.
        The reinforcement stage consists of two parts:
          - In the first part the player receives a number of reinforcements,
            based on the territories he owns. He places them on the board one-
            by-one.
          - In the second part the player may return in reinforcement cards,
            after which he receives more reinforcements which he places on the
            board one-by-one.
        
        Args:
            player (Player): player who may reinforce.
        """
        n_reinforcements = self.board.reinforcements(player.player_id)
        for _ in range(n_reinforcements):
            self.board.add_armies(player.reinforce(), 1)
        card_set = player.turn_in_cards()
        if card_set is None:
            return
        n_extra = self.cards[player.player_id].turn_in(card_set)
        for _ in range(n_extra):
            self.board.add_armies(player.reinforce(), 1)

    def attack(self, player):
        """
        Handle the attack phase of a player.
        The player may perform as many attacks as he wishes.
        
        Args:
            player (Player): player that may attack.
        """
        did_win = False
        while True:
            attack = player.attack(did_win)
            if attack is None:
                break
            if not self.current_player_id == self.board.owner(attack[0]):
                raise Exception('Invalid attack!')
            if self.board.attack(*attack):
                did_win = True
        if did_win:
            self.cards[player.player_id].receive()

    def fortify(self, player):
        """
        Handle the fortification phase of a player.
        
        Args:
            player (Player): player that may fortify.
        """
        fortification = player.fortify()
        if fortification is not None:
            if not self.current_player_id == self.board.owner(fortification[0]):
                raise Exception('Invalid fortification!')
            self.board.fortify(*fortification)

    # ================== #
    # == Plot methods == #
    # ================== #           

    def plot(self):
        """ Plot the current game on a board. """
        self.board.plot_board()
        self.plot_table()
        self.plot_turn()
        plt.axis('off')
        plt.show()

    def plot_table(self):
        """ Plot the stats table. """
        text = ['Player: ter arm mis']

        for player in self.players:
            pid = player.player_id
            text.append('{c:6}:{r:4} {a:3} {m:2.2f}'.format(
                c=definitions.player_colors[pid],
                r=self.board.n_territories(pid),
                a=self.board.n_armies(pid),
                m=self.missions[pid].score(self.board))
                        .expandtabs())

        font0 = FontProperties()
        font0.set_family('monospace')

        # Left bottom
        plt.text(-50, 1160, '\n'.join(text), fontproperties=font0)

    def plot_turn(self):
        """ Plot the turn. """
        if self.current_player >= 0:
            if self.has_ended():
                color = self.winner().color
                mission = self.winner().mission.description
                content = 'Winner: {p} - {m}\nTotal turns {nr}'.format(nr=self.turn, p=color, m=mission)
            else:
                color = definitions.player_colors[self.current_player_id]
                mission = self.missions[self.current_player_id].description
                content = 'Turn {nr}: {p} - {m}'.format(nr=self.turn, p=color, m=mission)
        else:
            content = 'Pre-game'

        # Top left
        plt.text(-50, 0, content, fontsize=12)
