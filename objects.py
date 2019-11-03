from numba import jit, jit_module, jitclass
from abc import ABC, abstractmethod
import random
from collections import Sequence, MutableSet


class Board:
    def __init__(self, num_players):
        self.play_state = 1
        self.draw_state = 1
        self.deck = Deck(self)
        self.num_players = num_players
        self.hands = [Hand(player_num) for player_num in range(num_players)]
        self.keeps = [Keep(player_num) for player_num in range(num_players)]
        self.turn_num = 0
        self.player_state = 0
        self.cards_played = 0
        self.cards_drawn = 0
        self.goals = []

    def inc_cards_played(self):
        self.cards_played += 1
        if self.cards_played > self.play_state:
            raise self.TooManyCardsPlayed(f"Somehow someone played more than {self.play_state} cards this turn.")
        if self.cards_played == self.play_state:
            self.inc_player_state()
            # In strict rules, the turn ends when you play your last card. Some players are lenient on
            # this and allow people to take a free action after their last play.
            self.cards_played = 0

    def inc_player_state(self):
        self.turn_num += 1
        self.player_state = self.turn_num % self.num_players

    class TooManyCardsPlayed(Exception):
        def __init__(self, *args, **kwargs):
            super(Board.TooManyCardsPlayed, self).__init__(*args, *kwargs)


class Card:
    def __init__(self, board, name):
        # A card has to be connected to a board object. This way each card must be unique to the
        # game it is in, and is always connected to the game that it's initialized for.
        self._board = board
        self._name = name

    @property
    def board(self):
        return self._board

    @property
    def name(self):
        return self._name

    @abstractmethod
    def do(self):
        pass

        # Do some stuff to the board

    def play(self):
        self.do()
        self.board.inc_cards_played()

    def __hash__(self):
        return hash(self.name + repr(self.board))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'{self.name}'


class Keeper(Card):

    def do(self):
        tar_keep = self.board.keeps[self.board.player_state]
        tar_hand = self.board.hands[self.board.player_state]
        tar_keep.add(self)
        tar_hand.discard(self)


class Deck(Sequence):
    def __init__(self, board):
        super(Deck, self).__init__()
        self.values = []
        self._board = board

    @property
    def board(self):
        return self._board

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)


class Hand(set):

    def __init__(self, player_num):
        super(Hand, self).__init__()
        self.player_num = player_num
        self.cards = set()


class Keep(set):

    def __init__(self, player_num):
        super(Keep, self).__init__()
        self.player_num = player_num
        self.cards = set()
