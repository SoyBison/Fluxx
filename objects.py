from abc import abstractmethod
from collections import MutableSequence, MutableSet
# noinspection PyProtectedMember,PyProtectedMember
from typing import Iterator, _T_co, _T
from random import randint, shuffle

from assets import *


class Board:
    def __init__(self, num_players):
        self.deck = Deck(self)
        self.trash = Deck.discard_creator(self)
        self.num_players = num_players
        self.hands = [Hand(player_num, self) for player_num in range(num_players)]
        self.keeps = [Keep(player_num) for player_num in range(num_players)]
        self.turn_num = 0
        self.player_state = 0
        self.cards_played = 0
        self.cards_drawn = 0
        self.goals = GoalSpace()
        self.rules = RuleSpace()
        self.special_turn = None
        self.numeral = 0
        self.draw_bonuses = []
        self.play_bonuses = []
        self.card_set = self.deck.values
        self.bonus_plays = [0 for _ in range(num_players)]
        self.special_actions = set()
        self.action_type = 'normal'
        self.limit_state = None

    def inc_cards_played(self):
        self.cards_played += 1
        if self.cards_played >= self.play_state:
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
    def options(self):
        return {'normal': list(self.hands[self.active_player]) + list(self.special_actions),
                'handlimit': list(self.hands[self.active_player]),
                'keeperlimit': list(self.keeps[self.active_player]),
                'goalmill': [card for card in list(self.hands[self.active_player]) if isinstance(card, Goal)],
                'recycling': list(self.keeps[self.active_player])
                }[self.action_type]

    @property
    def info(self):
        return {'draws': self.draw_state, 'plays': self.play_state, 'player': self.active_player,
                'keeps': self.keeps, 'goals': self.goals, 'rules': self.rules,
                'discard': self.trash, 'hand': self.hands[self.player_state], 'options': self.options,
                'actiontype': self.action_type}

    @property
    def draw_state(self):
        return sum(self.draw_bonuses) + 1 + self.numeral

    @property
    def active_player(self):
        if self.action_type.endswith('limit'):
            return self.limit_state
        else:
            return self.player_state

    @property
    def play_state(self):
        return sum(self.play_bonuses) + 1 + self.numeral

    def action(self, option):
        hand = self.hands[self.active_player]
        keep = self.keeps[self.active_player]
        if self.action_type == 'normal':
            choice = self.options[option]
            if not isinstance(choice, FreeAction):
                choice.do()
                self.inc_cards_played()
            if isinstance(choice, FreeAction):
                choice.effect()

        if self.action_type == 'handlimit':
            if isinstance(option, int):
                option = [option]
            for choice in option:
                card = self.options[choice]
                hand.discard(card)

        if self.action_type == 'keeperlimit':
            if isinstance(option, int):
                option = [option]
            for choice in option:
                card = self.options[choice]
                keep.discard(card)

        if self.action_type == 'goalmill':
            if isinstance(option, int):
                option = [option]
            for choice in option:
                card = self.options[choice]
                hand.discard(card)
                hand.draw(1)

        if self.action_type == 'recycling':
            self.options[option].trash()
            recyclingcard = [card for card in self.card_set if card.tag == 'fa_recycling'][0]
            hand.draw(3 + recyclingcard.numeral)

        self.check_goal()


class Card:
    def __init__(self, board, name):
        # A card has to be connected to a board object. This way each card must be unique to the
        # game it is in, and is always connected to the game that it's initialized for.
        self._board = board
        self._name = name
        self.numeral = None

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
        hand = self.board.hands[self.board.player_state]
        if self in hand:
            hand.cards.discard(self)

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
        tar_hand.cards.discard(self)

    def trash(self):
        tar_keep = [keep for keep in self.board.keeps if self in keep][0]
        tar_keep.discard(self)
        self.board.trash.append(self)


class Deck(MutableSequence):
    def __init__(self, board):
        super(Deck, self).__init__()
        self.values = []
        rule_cats = {'Draw': Draw, 'Play': Play, 'Limit': Limit, 'Free Actions': FreeAction,
                     'Effect': Effect, 'Start': Start}
        action_cats = {}  # TODO: Keep this up to date
        for name in keepers:
            self.values.append(Keeper(self.board, name))
        for tag in goals.items():
            self.values.append(Goal(board, tag))

        for cat in rules:
            ruleset = list(rules[cat].items())
            for name, tag in ruleset:
                self.values.append(rule_cats[cat](self.board, name, tag))
        for cat in actions:
            ruleset = list(rules[cat].items())
            for name, tag in ruleset:
                self.values.append(action_cats[cat](self.board, name, tag))

        shuffle(self.values)
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
        self.values[key] = value

    def insert(self, index: int, value: _T):
        self.values.insert(index, value)

    def __delitem__(self, key):
        del self.values[key]

    def draw(self):
        return self.pop(0)


class Hand(MutableSet):

    def add(self, x: _T) -> None:
        if isinstance(x, Card):
            self.cards.add(x)
        else:
            raise TypeError('A hand can only contain cards.')

    def discard(self, x: Card) -> None:
        self.cards.discard(x)
        self.board.trash.append(x)

    def __contains__(self, x: object) -> bool:
        if isinstance(x, Card):
            return x.name in {y.name for y in self.cards}

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self.cards)

    def __init__(self, player_num, board, _draw=True):
        super(Hand, self).__init__()
        self.player_num = player_num
        self.cards = set()
        self.board = board
        if _draw:
            self.draw(3)

    def draw(self, amount):
        for _ in range(amount):
            self.add(self.board.deck.draw())

    @classmethod
    def temphand(cls, size, board):
        h = Hand(-1, board, _draw=False)
        h.draw(size)
        return h


class CardSpace(MutableSet):
    def add(self, x: _T) -> None:
        if isinstance(x, self.kind):
            self.cards.add(x)
        else:
            raise TypeError('A hand can only contain cards.')

    def discard(self, x: Card) -> None:
        self.cards.discard(x)

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
        self.numeral = 0

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
            qualifiers = [s >= 5 + self.numeral for s in stats]
            return fluxx_most_check(target, qualifiers, stats)

        def _notv(target: int, g: Goal):
            return not any(['Television' in k for k in g.board.keeps]) and 'Brain' in g.board.keeps[target]

        def _tencards(target: int, g: Goal):
            stats = [len(h) for h in g.board.hands]
            qualifiers = [s >= 10 + self.numeral for s in stats]
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
        self.last = None

    @property
    def draw_rule(self):
        return self._draw_rule - 1 + self.numeral

    def enact(self):
        self.board.draw_bonuses.append(self.draw_rule)
        self.last = self.draw_rule

    def repeal(self):
        self.board.draw_bonuses.remove(self.last)
        self.last = None

    def rule(self):
        self.board.draw_bonuses.remove(self.last)
        self.board.draw_bonuses.append(self.draw_rule)
        self.last = self.draw_rule


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
        if self.play_rule > 0:
            self.board.play_bonuses.append(self.play_rule)

    def repeal(self):
        if self.play_rule > 0:
            self.board.play_bonuses.remove(self.play_rule)
        else:
            self.board.play_bonuses.remove(self.last_num)

    def rule(self):
        if self.play_rule <= 0:
            tarhand = self.board.hands[self.board.player_state]
            if self.last_num:
                self.board.play_bonuses.remove(self.last_num)
            self.board.play_bonuses.append(len(tarhand) + self.play_rule)
            self.last_num = len(tarhand) + self.play_rule


class Limit(Rule):
    def __init__(self, board, name, tag):
        super(Limit, self).__init__(board, name)
        number, tar_space = tag
        self._number = number
        self.numeral = 0
        self.tar_space = tar_space
        self.tar_list = self.board.keeps if self.tar_space is Keep else self.board.hands

    @property
    def number(self):
        return self._number + self.numeral

    def enact(self):
        pass

    def repeal(self):
        pass

    def rule(self):
        def checkr(space: CardSpace):
            if len(space > self.number):
                return True
            elif len(space <= self.number):
                return False

        limit_fails = [sp.player_num for sp in filter(checkr, self.tar_list)]

        if limit_fails:
            player = limit_fails[0]
            self.board.action_type = 'limit'
            self.board.limit_state = player
        else:
            self.board.limit_state = None


class Effect(Rule):
    def __init__(self, board, name, tag):
        super(Effect, self).__init__(board, name)
        self.tag = tag
        self._marker = 1
        if self.tag in {'e_partybonus', 'e_poorbonus', 'e_richbonus'}:
            self.numeral = 0
        self.last = None

    @property
    def marker(self):
        return self._marker + self.numeral

    def enact(self):
        if self.tag in {'e_partybonus', 'e_poorbonus', 'e_richbonus'}:
            self.last = self.marker
        if self.tag == 'e_inflation':
            for card in self.board.card_set:
                if card.numeral is not None:
                    card.numeral = 1
        if self.tag == 'e_doubleagenda':
            self.board.goals.max_size = 2

    def repeal(self):
        if self.tag in {'e_partybonus', 'e_poorbonus'}:
            self.board.draw_bonuses.remove(self.last)
            self.last = None
        if self.tag in {'e_partybonus', 'e_richbonus'}:
            self.board.play_bonuses.remove(self.last)
            self.last = None
        if self.tag == 'e_inflation':
            for card in self.board.card_set:
                if card.numeral is not None:
                    card.numeral = 0
        if self.tag == 'e_doubleagenda':
            self.board.goals.max_size = 1

    def rule(self):
        if self.tag in {'e_inflation', 'e_doubleagenda'}:
            return None
        if self.tag in {'e_partybonus', 'e_poorbonus'}:
            self.board.draw_bonuses.remove(self.last)
            self.board.draw_bonuses.append(self.marker)
            self.last = self.marker
        if self.tag in {'e_partybonus', 'e_richbonus'}:
            self.board.play_bonuses.remove(self.last)
            self.board.play_bonuses.append(self.marker)
            self.last = self.marker


class Start(Rule):
    def __init__(self, board, name, tag):
        super(Start, self).__init__(board, name)
        self.tag = tag
        if tag in {'s_nohandbonus'}:
            self.numeral = 0
        self.last = None

    @property
    def size(self):
        if self.tag == 's_nohandbonus':
            return 3 + self.numeral
        else:
            raise TypeError(f'Card {self.name} does not have a size.')

    def enact(self):
        if self.tag in {'s_nohandbonus'}:
            self.board.draw_bonuses.append(self.size)
            self.last = self.size

    def repeal(self):
        if self.tag in {'s_nohandbonus'}:
            self.board.draw_bonuses.remove(self.last)
            self.last = self.size

    def rule(self):
        if self.tag in {'s_nohandbonus'}:
            self.board.draw_bonuses.remove(self.last)
            self.board.draw_bonuses.append(self.size)
            self.last = self.size
        if self.tag in {'s_firstplayrandom'}:
            curr_hand = self.board.hands[self.board.player_state]
            if self.board.cards_played == 0 and self.board.play_state > 1:
                curr_hand.do(randint(0, len(curr_hand)))


class FreeAction(Rule):
    def __init__(self, board, name, tag):
        super(FreeAction, self).__init__(board, name)
        self.tag = tag
        if self.tag in {'fa_recycling', 'fa_getonwithit'}:
            self.numeral = 0
        self.used = False
        self.last_used = None

    @property
    def size(self):
        if self.tag in {'fa_recycling', 'fa_getonwithit'}:
            return 3 + self.numeral
        else:
            raise TypeError(f'Card {self.name} does not have a size.')

    def enact(self):
        self.board.special_actions.add(self)

    def repeal(self):
        self.board.special_actions.discard(self)

    def rule(self):
        pass

    def effect(self):
        hand = self.board.hands[self.board.player_state]
        keep = self.board.keeps[self.board.player_state]
        self.used = True
        self.last_used = self.board.player_state
        if self.tag == 'fa_swapplaysfordraws':
            hand.draw(self.board.play_state - self.board.cards_played)
            for _ in range(self.board.play_state - self.board.cards_played):
                self.board.inc_cards_played()
        if self.tag == 'fa_mysteryplay':
            self.board.deck.draw().play()
        if self.tag == 'fa_goalmill':
            self.board.special_turn = 'goalmill'
        if self.tag == 'fa_getonwithit':
            if len(hand) > 0:
                for card in hand:
                    hand.discard(card)
                hand.draw(3)
            else:
                raise ValueError('You cannot use Get On With It! with an empty hand.')
        if self.tag == 'fa_recycling':
            if len(keep) > 0:
                self.board.special_turn = 'recycling'
            else:
                raise ValueError('You cannot use Recycling with an empty keep.')
