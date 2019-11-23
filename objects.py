from abc import abstractmethod
from collections import MutableSequence, MutableSet
# noinspection PyProtectedMember,PyProtectedMember
from typing import Iterator, _T_co, _T

from assets import *


class Board:
    def __init__(self, num_players):
        self.deck = Deck(self)
        self.trash = Deck.discard_creator(self)
        self.num_players = num_players
        self.hands = [Hand(player_num) for player_num in range(num_players)]
        self.keeps = [Keep(player_num) for player_num in range(num_players)]
        self.turn_num = 0
        self.player_state = 0
        self.cards_played = 0
        self.cards_drawn = 0
        self.goals = GoalSpace()
        self.rules = RuleSpace()
        self.special_turn = None
        self.draw_bonuses = []
        self.play_bonuses = []
        self.card_set = self.deck.values

    def inc_cards_played(self):
        self.cards_played += 1
        if self.cards_played > self.play_state:
            raise self.TooManyCardsPlayed(f"Somehow player {self.player_state} played more than {self.play_state} "
                                          f"cards this turn.")
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

    @property
    def info(self):
        return {'draws': self.draw_state, 'plays': self.play_state, 'player': self.player_state, 'keeps': self.keeps,
                'goals': self.goals, 'rules': self.rules, 'discard': self.trash}

    @property
    def draw_state(self):
        return sum(self.draw_bonuses)

    @property
    def play_state(self):
        return sum(self.play_bonuses)


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
        pass  # Do some stuff to the board

    @abstractmethod
    def trash(self):
        pass  # do cleanup tasks

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

    def trash(self):
        tar_keep = [keep for keep in self.board.keeps if self in keep][0]
        tar_keep.discard(self)
        self.board.trash.append(self)


class Deck(MutableSequence):
    def __init__(self, board):
        super(Deck, self).__init__()
        self.targets = keepers + list(goals.items())
        for cat in rules:
            cardset = list(rules[cat].items())
            self.targets += cardset
        # TODO: Don't forget to add stuff to this as you add assets
        self.values = []
        self._board = board

    @property
    def board(self):
        return self._board

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    @classmethod
    def discard_creator(cls, board):
        disc = Deck(board)
        disc.values = []
        return disc

    def __setitem__(self, key, value):
        if isinstance(value, tuple):
            name, tag = value

            if 'Play' == name[:4]:
                self.values[key] = Play(self.board, value)
            if 'Draw' == name[:4]:
                self.values[key] = Draw(self.board, value)


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
        if isinstance(x, str):  # In Fluxx, Card Names are unique identifiers.
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
        self.cards = []  # This technically isn't totally appropriate, but it prevents us from having to target the goal
        # in some way to trash it. When there isn't a double agenda, there's only ever one goal in here anyway, and it's
        # inconsistent to pop the card then trash it.
        self.max_size = 1

    def add(self, x):
        if 1 == len(self) > self.max_size == 1:
            self.cards[0].trash()
        elif len(self) > self.max_size > 1:
            ...  # Do a special turn for removing a goal
        if isinstance(x, Goal):
            self.cards.append(x)
        else:
            raise TypeError(f'You Cannot Add a {type(x)} to the Goals List')


class Goal(Card):

    def do(self):
        self.board.goals.add(self)
        tar_hand = self.board.hands[self.board.player_state]
        tar_hand.discard(self)

    def trash(self):
        self.board.goals.discard(self)
        self.board.trash.append(self)

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

        def _anyfood(target: int, g: Goal):
            target = g.board.keeps[target]
            return any([food in target for food in foods])

        def _fivekeepers(target: int, g: Goal):
            stats = [len(k) for k in g.board.keeps]
            qualifiers = [s >= 5 for s in stats]
            return fluxx_most_check(target, qualifiers, stats)

        def _notv(target: int, g: Goal):
            return not any(['Television' in k for k in g.board.keeps]) and 'Brain' in g.board.keeps[target]

        def _tencards(target: int, g: Goal):
            stats = [len(h) for h in g.board.hands]
            qualifiers = [s >= 10 for s in stats]
            return fluxx_most_check(target, qualifiers, stats)

        tardic = {'_anyfood': _anyfood, '_fivekeepers': _fivekeepers, '_notv': _notv, '_tencards': _tencards}

        return tardic[req](player_num, self)


class RuleSpace(CardSpace):
    def __init__(self):
        super(RuleSpace, self).__init__(Rule)

    @property
    def ruleset(self):
        ruleset = [card.rule for card in self.cards]
        return ruleset


class Rule(Card):
    def do(self):
        self.board.rules.add(self)
        self.enact()

    def trash(self):
        self.board.rules.discard(self)
        self.repeal()

    @abstractmethod
    def rule(self):
        pass

    @abstractmethod
    def enact(self):
        pass

    @abstractmethod
    def repeal(self):
        pass


class Draw(Rule):
    def __init__(self, board, tag):
        name, draw_rule = tag
        super(Draw, self).__init__(board, name)
        self.numeral = 0
        self._draw_rule = draw_rule

    @property
    def draw_rule(self):
        return self._draw_rule - 1 + self.numeral

    def enact(self):
        self.board.draw_bonuses.append(self.draw_rule)

    def repeal(self):
        self.board.draw_bonuses.remove(self.draw_rule)

    def rule(self):
        pass


class Play(Rule):
    def __init__(self, board, tag):
        name, play_rule = tag
        super(Play, self).__init__(board, name)
        self.last_num = None
        self.numeral = 0
        self._play_rule = play_rule

    @property
    def play_rule(self):
        play_rule = self._play_rule
        if play_rule > 0:
            actual = play_rule - 1 + self.numeral
        elif play_rule == 0:
            actual = play_rule
        else:
            actual = play_rule - self.numeral
        return actual

    def enact(self):
        pass

    def repeal(self):
        self.board.play_bonuses.remove(self.play_rule)

    def rule(self):
        if self.play_rule <= 0:
            tarhand = self.play_rule
            if self.last_num:
                self.board.play_bonuses.remove(self.last_num)
            self.board.play_bonuses.append()
