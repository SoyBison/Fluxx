from typing import Iterator, _T_co, _T
from assets import *
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
        self.goals = GoalSpace()

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
        def __init__(self, *args):
            super(Board.TooManyCardsPlayed, self).__init__(*args)

    def check_goal(self):
        if self.goals:
            for goal in self.goals:
                winner = goal.evaluate()
                if winner:
                    raise self.Win(f'Player {winner}')

    class Win(Exception):
        def __init__(self, *args):
            super(Board.Win, self).__init__(*args)


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
        self.board.check_goal()

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


class Hand(MutableSet):

    def add(self, x: _T) -> None:
        if isinstance(x, Card):
            self.cards.add(x)
        else:
            raise TypeError('A hand can only contain cards.')

    def discard(self, x: _T) -> None:
        self.cards.discard(x)
        x.play()

    def __contains__(self, x: object) -> bool:
        if isinstance(x, Card):
            return x.name in {y.name for y in self.cards}

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self.cards)

    def __init__(self, player_num):
        super(Hand, self).__init__()
        self.player_num = player_num
        self.cards = set()


class CardSpace(MutableSet):
    def add(self, x: _T) -> None:
        if isinstance(x, self.kind):
            self.cards.add(x)
        else:
            raise TypeError('A hand can only contain cards.')

    def discard(self, x: _T) -> None:
        self.cards.discard(x)
        x.play()

    def __contains__(self, x: object) -> bool:
        if isinstance(x, self.kind):
            return x.name in {y.name for y in self.cards}
        if isinstance(x, str): # In Fluxx, Card Names are unique identifiers.
            return x in {y.name for y in self.cards}

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self.cards)

    def __init__(self, kind):
        super(CardSpace, self).__init__()
        self.cards = set()
        assert issubclass(kind, Card)
        self.kind = kind


class Keep(CardSpace):

    def __init__(self, player_num):
        super(Keep, self).__init__(Keeper)
        self.player_num = player_num
        self.cards = set()


class GoalSpace(CardSpace):

    def __init__(self):
        super(GoalSpace, self).__init__(Goal)
        self.cards = set()
        self.max_size = 1

    def add(self, x):
        if 1 == len(self) > self.max_size == 1:
            self.cards.pop()
        elif len(self) > self.max_size > 1:
            ...  # Do a special turn for removing a goal
        if isinstance(x, Goal):
            self.cards.add(x)
        else:
            raise TypeError(f'You Cannot Add a {type(x)} to the Goals List')


class Goal(Card):

    def do(self):
        self.board.goals.add(self)

    def __init__(self, board, tag):
        """
        tag should be stored as an 'item' call from a dict.items().
        :param board: Board
        :param tag: tuple
        """
        name, reqs = tag
        super(Goal, self).__init__(board, name)
        self._reqs = reqs

    @property
    def reqs(self):
        return self._reqs

    @property
    def evaluate(self):
        for player_num in range(self.board.num_players):
            quals = []
            for req in self.reqs:  # This should pick a function based on the requirements.
                if req[0] == '_':
                    quals.append(self.exotic_check(player_num, req))
                else:
                    quals.append(self.normal_check(req, player_num))
            if all(quals):
                return player_num
        return None

    def normal_check(self, req, player_num):
        keep = self.board.keeps[player_num]
        return req in keep

    def exotic_check(self, req, player_num):

        def fluxx_most_check(target, qualifiers, stats):
            if sum(qualifiers) > 1:
                max_keepers = max(stats)
                winners = [s >= max_keepers for s in stats]
                if sum(winners) > 1:
                    return False
                else:
                    return winners[target]
            if sum(qualifiers) == 1:
                return qualifiers[target]
            else:
                return False

        def _anyfood(target: int):
            target = self.board.keeps[target]
            return any([food in target for food in foods])

        def _fivekeepers(target: int):
            stats = [len(k) for k in self.board.keeps]
            qualifiers = [s >= 5 for s in stats]
            return fluxx_most_check(target, qualifiers, stats)

        def _notv(target: int):
            return not any(['Television' in k for k in self.board.keeps])

        def _tencards(target: int):
            stats = [len(h) for h in self.board.hands]
            qualifiers = [s >= 10 for s in stats]
            return fluxx_most_check(target, qualifiers, stats)

        def tar_func(o):
            pass

        exec(f'tar_func = {req}')
        return tar_func(player_num)


