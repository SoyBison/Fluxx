"""
Author: Coen D. Needell
Copyright: Looney Labs

This file contains all of the 'meat and potatoes' of the game. It contains all the objects that the game engine
interacts with and does all of the computational work of the game. It's a card game though, so that's not too hard.
The main purpose is for a Board object to act as a finite state machine which can be controlled using board.action().
"""

from abc import abstractmethod
from collections.abc import MutableSequence, MutableSet
from itertools import cycle, chain
from math import ceil
from random import shuffle, choice

from assets import *


class Board:
    """
    The Board object houses all of the information about the current game. Each card in the game has to be connected
    to a Board object.
    :type num_players: int The number of players playing the game.
    """
    def __init__(self, num_players):

        self.deck = Deck(self)
        self.hands = [Hand(player_num, self) for player_num in range(num_players)]
        self.keeps = [Keep(player_num, self) for player_num in range(num_players)]
        self.hands[0].draw(1)
        self.trash = Deck.discard_creator(self)
        self.num_players = num_players
        self.turn_num = 0
        self.player_state = 0
        self.cards_played = 0
        self.cards_drawn = 1
        self.goals = GoalSpace(self)
        self.rules = RuleSpace(self)
        self.temp_cards_played = 0
        self.special_turn = None
        self.numeral = 0
        self.draw_bonuses = []
        self.play_bonuses = []
        self.bonus_plays = [0 for _ in range(num_players)]
        self.special_actions = set()
        self.action_type = 'normal'
        self.limit_state = None
        self.temphands = [Hand.temphand(0, self)]
        self.free_turn = False
        self.exchange_space = None
        self.mysteryplay = None

    def inc_cards_played(self):
        self.cards_played += 1
        freeturncard = [card for card in self.card_set if card.tag == 'a_anotherturn'][0]
        if (self.cards_played >= self.play_state and self.action_type == 'normal') or len(self.curr_hand) == 0:
            if not self.free_turn:
                self.inc_player_state()
                self.curr_hand.draw(self.draw_state)
                freeturncard.used = False
            else:
                self.curr_hand.draw(self.draw_state)
                self.free_turn = False
            # In strict rules, the turn ends when you play your last card. Some players are lenient on
            # this and allow people to take a free action after their last play.
            self.cards_played = 0
            self.cards_drawn = self.draw_state
            self.check_starts()

    class IllegalMove(Exception):
        def __init__(self, board, *args):
            super(Board.IllegalMove, self).__init__(*args)
            self.board = board

    class IllegalPlay(IllegalMove):
        def __init__(self, board, *args):
            super(Board.IllegalPlay, self).__init__(board, *args)
            self.board.cards_played -= 1

    def inc_player_state(self):
        self.turn_num += 1
        self.player_state = self.turn_num % self.num_players

    class TooManyCardsPlayed(Exception):
        def __init__(self, *args):
            super(Board.TooManyCardsPlayed, self).__init__(*args)

    def check_goal(self):
        if self.goals:
            for goal in self.goals:
                winner = goal.evaluate
                if winner is not None:
                    raise Board.Win(f'Player {winner}')

    def check_rules(self):
        if self.rules:
            for rule in self.rules.ruleset:
                rule()
        if self.draw_state > self.cards_drawn > 0:
            self.curr_hand.draw(self.draw_state - self.cards_drawn)
            self.cards_drawn += (self.draw_state - self.cards_drawn)
        if self.cards_played >= self.play_state:
            self.inc_cards_played()

    class Win(Exception):
        def __init__(self, *args):
            super(Board.Win, self).__init__(*args)

    def check_starts(self):
        starts = [rule for rule in self.rules if isinstance(rule, Start)]
        for card in starts:
            card.start()

    @property
    def card_set(self):
        cards_in_hand = list(chain.from_iterable(self.hands))
        cards_in_keeps = list(chain.from_iterable(self.hands))
        cards_not_in_play = self.deck.values + self.trash.values
        return cards_in_hand + cards_in_keeps + cards_not_in_play + list(self.rules.cards) + list(self.goals.cards)
            
    @property
    def curr_hand(self):
        return self.hands[self.active_player]

    @property
    def curr_keep(self):
        return self.keeps[self.active_player]

    @property
    def cards_seen(self):
        return list(self.curr_hand) + list(self.trash) + list(self.rules) + list(self.goals)

    @property
    def options(self):
        if self.action_type == 'normal':
            return list(self.curr_hand) + list(self.special_actions)
        elif self.action_type == 'handlimit':
            return list(self.curr_hand)
        elif self.action_type == 'keeperlimit':
            return list(self.curr_keep)
        elif self.action_type == 'goalmill':
            return [card for card in list(self.curr_hand) if isinstance(card, Goal)]
        elif self.action_type == 'recycling':
            return list(self.curr_keep)
        elif self.action_type == 'play2':
            return list(self.temphands[-1])
        elif self.action_type == 'zap':
            return list(chain.from_iterable(self.keeps)) + list(self.goals) + list(self.rules)
        elif self.action_type == 'goalremove':
            return list(self.goals)
        elif self.action_type == 'rotate':
            return [1, -1]
        elif self.action_type == 'doitagain':
            return [card for card in self.trash if (isinstance(card, Action) or isinstance(card, Rule))]
        elif self.action_type == 'steal':
            return list(chain.from_iterable(keep for keep in self.keeps if keep.player_num != self.active_player))
        elif self.action_type == 'simplify':
            return list(self.rules)
        elif self.action_type == 'trash':
            return list(chain.from_iterable(self.keeps))
        elif self.action_type == 'exchange1':
            return list(chain.from_iterable(keep for keep in self.keeps if keep.player_num != self.active_player))
        elif self.action_type == 'exchange2':
            return list(self.curr_keep)
        elif self.action_type == 'trade':
            return list(p for p in range(self.num_players) if p != self.active_player)
        elif self.action_type == 'usetake':
            return [player for player in list(range(self.num_players)) if player != self.active_player]

    @property
    def info(self):
        remaining = self.play_state - self.cards_played
        if remaining < 0:
            remaining = 0
        return {'draws': self.draw_state, 'plays': self.play_state, 'player': self.active_player,
                'keeps': self.keeps, 'goals': self.goals, 'rules': self.rules,
                'discard': self.trash, 'hand': self.hands[self.player_state], 'options': self.options,
                'actiontype': self.action_type, 'mystery': self.mysteryplay,
                'remaining': remaining, 'drawn': self.cards_drawn}

    @property
    def draw_state(self):
        return sum(self.draw_bonuses) + 1 + (self.numeral * (not any([isinstance(rule, Draw) for rule in self.rules])))

    @property
    def active_player(self):
        if self.action_type.endswith('limit') and self.limit_state is not None:
            return self.limit_state
        else:
            return self.player_state

    @property
    def play_state(self):
        return sum(self.play_bonuses) + 1 + (self.numeral * (not any([isinstance(rule, Play) for rule in self.rules])))

    def action(self, option):
        hand = self.curr_hand
        keep = self.curr_keep
        self.check_rules()
        if self.action_type == 'normal':
            pick = self.options[option]
            if pick in self.curr_hand:
                pick.play()
                self.inc_cards_played()
            elif isinstance(pick, FreeAction):
                pick.effect()

        elif self.action_type == 'handlimit':
            card = self.options[option]
            hand.discard(card)

        elif self.action_type == 'keeperlimit':
            card = self.options[option]
            keep.discard(card)

        elif self.action_type == 'goalmill':
            if isinstance(option, int):
                option = [option]
            for pick in option:
                card = self.options[pick]
                hand.discard(card)
                hand.draw(1)
            self.action_type = 'normal'

        elif self.action_type == 'recycling':
            self.options[option].trash()
            recyclingcard = [card for card in self.card_set if card.tag == 'fa_recycling'][0]
            hand.draw(3 + recyclingcard.numeral)
            self.action_type = 'normal'

        elif self.action_type == 'play2':
            tarhand = self.temphands[-1]
            card = self.options[option]
            card.play()
            if card in tarhand:
                tarhand.discard(card)
            tarhand.cards_played += 1
            if tarhand.cards_played == 2 + ('Inflation' in {rule.name for rule in self.rules}):
                self.action_type = 'normal'

        elif self.action_type == 'everybody1':
            everybodycard = [card for card in self.card_set if card.tag == 'a_everybody1'][0]
            temphand = self.temphands[-1]
            tarplayer = temphand.cards_played // (1 + everybodycard.numeral)
            tarhand = self.hands[tarplayer]
            if everybodycard.numeral:
                for pick in option:
                    card = self.options[pick]
                    temphand.discard(card)
                    tarhand.add(card)
                    temphand.cards_played += 1
            else:
                card = self.options[option]
                temphand.discard(card)
                tarhand.add(card)
                temphand.cards_played += 1

            if len(temphand) == 0 or temphand.cards_played >= (self.num_players * (1 + everybodycard.numeral)):
                self.action_type = 'normal'

        elif self.action_type == 'zap':
            pick = self.options[option]
            if isinstance(pick, Keeper):
                tarkeep = [keep for keep in self.keeps if pick in keep][0]
                tarkeep.cards.discard(pick)
            if isinstance(pick, Goal):
                self.goals.discard(pick)
            if isinstance(pick, Rule):
                self.rules.discard(pick)
            self.curr_hand.add(pick)
            self.action_type = 'normal'

        elif self.action_type == 'goalremove':
            pick = self.options[option]
            pick.trash()
            self.action_type = 'normal'

        elif self.action_type == 'rotate':
            pick = self.options[option]
            assert isinstance(pick, int)  # This is to shut up my IDE's typechecker
            temp = [[]] * self.num_players
            for hand in self.hands:
                for card in hand:
                    temp[hand.player_num].append(card)
            for player in range(self.num_players):
                tarplayer = (player + pick) % self.num_players
                for card in temp[player]:
                    tarhand = self.hands[tarplayer]
                    tarhand.add(card)
            self.action_type = 'normal'

        elif self.action_type == 'doitagain':
            pick = self.options[option]
            self.action_type = 'normal'
            pick.play()
            self.trash.remove(pick)
            self.trash.append(pick)

        elif self.action_type == 'steal':
            pick = self.options[option]
            tarkeep = [keep for keep in self.keeps if pick in keep][0]
            tarkeep.cards.discard(pick)
            self.curr_keep.add(pick)
            self.action_type = 'normal'

        elif self.action_type == 'simplify':
            if option:
                if not isinstance(option, iter):
                    option = [option]
                if len(option) >= ceil(len(self.rules) / 2):
                    raise Board.IllegalMove('You can only remove up to half of the Rule cards in play.')
                for pick in option:
                    pick = self.options[pick]
                    pick.trash()
            self.action_type = 'normal'

        elif self.action_type == 'trash':
            if len(self.options) > 0:
                pick = self.options[option]
                pick.trash()
            self.action_type = 'normal'

        elif self.action_type == 'exchange1':
            if len(self.options) > 0 and len(self.curr_keep) > 0:
                pick = self.options[option]
                tarhand = [hand for hand in self.hands if pick in hand][0]
                tarhand.cards.discard(pick)
                self.exchange_space = tarhand.player_num, pick
                self.action_type = 'exchange2'
            else:
                self.action_type = 'normal'

        elif self.action_type == 'exchange2':
            pick = self.options[option]
            tarplayer, other = self.exchange_space
            self.exchange_space = None
            self.curr_hand.add(other)
            self.curr_hand.cards.discard(pick)
            tarhand = self.hands[tarplayer]
            tarhand.add(pick)
            self.action_type = 'normal'

        elif self.action_type == 'trade':
            pick = self.options[option]  # This seems weird, but it's because it'll
            # throw an exception for the engine to catch automatically.
            temp = [[], []]
            assert isinstance(pick, int)
            tarhand = self.hands[pick]
            for card in self.curr_hand:
                temp[0].append(card)
            for card in tarhand:
                temp[1].append(card)
            for card in temp[0]:
                tarhand.add(card)
                self.curr_hand.discard(card)
            for card in temp[1]:
                self.curr_hand.add(card)
                tarhand.discard(card)
            self.action_type = 'normal'

        elif self.action_type == 'usetake':
            pick = self.options[option]
            assert isinstance(pick, int)
            tarhand = self.hands[pick]
            card = choice(list(tarhand))
            card.play()
            self.action_type = 'normal'

        self.check_goal()
        self.check_rules()


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
        self.do()
        self.remove_from_hand()

    def remove_from_hand(self):
        for hand in self.board.hands:
            if self in hand:
                hand.cards.discard(self)

    def trash_from_hand(self):
        for hand in self.board.hands:
            if self in hand:
                hand.discard(self)

    def __hash__(self):
        return hash(self.name + repr(self.board))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'{self.name}'


class Keeper(Card):

    def do(self):
        tar_keep = self.board.curr_keep
        tar_hand = self.board.curr_hand
        tar_keep.add(self)
        tar_hand.cards.discard(self)

    def trash(self):
        tar_keep = [keep for keep in self.board.keeps if self in keep][0]
        tar_keep.discard(self)
        self.board.trash.append(self)

    def discard_from_keep(self):
        tarkeep = [keep for keep in self.board.keeps if self in keep][0]
        tarkeep.discard(self)

    def __init__(self, board, name):
        super(Keeper, self).__init__(board, name)
        self.tag = name


class Deck(MutableSequence):
    def __init__(self, board):
        super(Deck, self).__init__()
        self.values = []
        self._board = board
        rule_cats = {'Draw': Draw, 'Play': Play, 'Limit': Limit, 'Free Action': FreeAction,
                     'Effect': Effect, 'Start': Start}
        for name in keepers:
            self.values.append(Keeper(self.board, name))
        for tag in goals.items():
            self.values.append(Goal(board, tag))

        for cat in rules:
            ruleset = list(rules[cat].items())
            for name, tag in ruleset:
                self.values.append(rule_cats[cat](self.board, name, tag))
        for name, tag in actions.items():
            self.values.append(Action(self.board, name, tag))

        shuffle(self.values)

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

    def insert(self, index: int, value):
        self.values.insert(index, value)

    def __delitem__(self, key):
        del self.values[key]

    def draw(self):
        if len(self) == 0:
            self.values = self.board.trash.values
            self.board.trash.values = []
            shuffle(self.values)

        return self.pop(0)


class Hand(MutableSet):

    def add(self, x: Card) -> None:
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

    def __iter__(self):
        return iter(self.cards)

    def __init__(self, player_num, board, _draw=True):
        super(Hand, self).__init__()
        self.player_num = player_num
        self.cards = set()
        self.board = board
        if _draw:
            self.draw(3)
        self.cards_played = None

    def draw(self, amount):
        for _ in range(amount):
            self.add(self.board.deck.draw())

    @classmethod
    def temphand(cls, size, board):
        h = Hand(-1, board, _draw=False)
        h.draw(size)
        h.cards_played = 0
        return h


class CardSpace(MutableSet):
    def add(self, x: Card) -> None:
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

    def __iter__(self):
        return iter(self.cards)

    def __init__(self, kind, board):
        super(CardSpace, self).__init__()
        self.cards = set()
        assert issubclass(kind, Card)
        self.kind = kind
        self._board = board

    @property
    def board(self):
        return self._board


class Keep(CardSpace):

    def __init__(self, player_num, board):
        super(Keep, self).__init__(Keeper, board)
        self.player_num = player_num
        self.cards = set()


class GoalSpace(CardSpace):

    def __init__(self, board):
        super(GoalSpace, self).__init__(Goal, board)
        self.cards = []  # This technically isn't totally appropriate, but it prevents us from having to target the goal
        # in some way to trash it. When there isn't a double agenda, there's only ever one goal in here anyway, and it's
        # inconsistent to pop the card then trash it.
        self.max_size = 1

    def add(self, x):
        if 1 == len(self) and self.max_size == 1:
            self.cards[0].trash()
        elif len(self) > self.max_size > 1:
            self.board.action_type = 'goalremove'
        if isinstance(x, Goal):
            self.cards.append(x)
        else:
            raise TypeError(f'You Cannot Add a {type(x)} to the Goals List')

    def remove(self, x):
        self.cards.remove(x)

    def discard(self, x: Card):
        self.cards.remove(x)


class Goal(Card):

    def do(self):
        self.board.goals.add(self)
        tar_hand = self.board.curr_hand
        tar_hand.discard(self)

    def trash(self):
        self.board.goals.remove(self)
        self.board.trash.append(self)

    def __init__(self, board, tag):
        """
        tag should be stored as an 'item' call from a dict.items().
        :param board: Board
        :param tag: tuple
        """
        name, reqs = tag
        self.tag = tag
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
                if req.startswith('_'):
                    quals.append(self.exotic_check(req, player_num))
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
            return sum([food in target for food in foods]) > self.numeral

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
    def __init__(self, board):
        super(RuleSpace, self).__init__(Rule, board)

    @property
    def ruleset(self):
        ruleset = [card.rule for card in self.cards]
        return ruleset


class Rule(Card):
    def do(self):
        self.enact()
        self.board.rules.add(self)
        self.remove_from_hand()

    def trash(self):
        self.board.rules.discard(self)
        self.board.trash.append(self)
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
    def __init__(self, board, name, tag):
        draw_rule = tag
        self.tag = name
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
        deadrules = []
        for rule in self.board.rules:
            if isinstance(rule, Draw):
                deadrules.append(rule)
        for rule in deadrules:
            rule.trash()

    def repeal(self):
        self.board.draw_bonuses.remove(self.last)
        self.last = None

    def rule(self):
        self.board.draw_bonuses.remove(self.last)
        self.board.draw_bonuses.append(self.draw_rule)
        self.last = self.draw_rule


class Play(Rule):
    def __init__(self, board, name, tag):
        play_rule = tag
        self.tag = name
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
            actual = play_rule - 1
        else:
            actual = play_rule - self.numeral - 1
        return actual

    def enact(self):
        if self.play_rule > 0:
            self.board.play_bonuses.append(self.play_rule)
        temp = []
        self.last_num = self.play_rule
        for rule in self.board.rules:
            if isinstance(rule, Play):
                temp.append(rule)
        for rule in temp:
            rule.trash()

    def repeal(self):
        self.board.play_bonuses.remove(self.last_num)

    def rule(self):
        if self.play_rule <= 0:
            tarhand = self.board.curr_hand
            if self.last_num:
                self.board.play_bonuses.remove(self.last_num)
            self.board.play_bonuses.append(len(tarhand) + self.play_rule)
            self.last_num = len(tarhand) + self.play_rule
            if self.play_rule < 0 and len(self.board.curr_hand) == 1:
                self.board.curr_hand.draw(1)
        else:
            self.board.play_bonuses.remove(self.last_num)
            self.board.play_bonuses.append(self.play_rule)
            self.last_num = self.play_rule


class Limit(Rule):
    def __init__(self, board, name, tag):
        super(Limit, self).__init__(board, name)
        number, tar_space = tag
        self.tag = tag
        self._number = number
        self.numeral = 0
        if tar_space == 'Hand':
            self.tar_space = Hand
        if tar_space == 'Keep':
            self.tar_space = Keep
        self.tar_list = None

    @property
    def number(self):
        return self._number + self.numeral

    def enact(self):
        pass

    def repeal(self):
        pass

    def rule(self):
        self.tar_list = self.board.keeps if self.tar_space is Keep else self.board.hands

        def checkr(space):
            if len(space) > self.number and space.player_num != self.board.player_state:
                return True
            elif len(space) <= self.number:
                return False

        limit_fails = [sp.player_num for sp in filter(checkr, self.tar_list)]

        if limit_fails:
            player = limit_fails[0]
            if self.tar_space == Keep:
                self.board.action_type = 'keeperlimit'
            else:
                self.board.action_type = 'handlimit'
            self.board.limit_state = player
        else:
            self.board.limit_state = None
            self.board.action_type = 'normal'


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
        if self.tag == 'e_inflation':
            for card in self.board.card_set:
                if card.numeral is not None:
                    card.numeral = 1
            self.board.numeral = 1
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
            self.board.numeral = 0
        if self.tag == 'e_doubleagenda':
            self.board.goals.max_size = 1

    def rule(self):

        if self.tag == 'e_partybonus' and any([card.name == 'Party' for card in chain.from_iterable(self.board.keeps)]):
            self.board.draw_bonuses.append(self.marker)
            self.board.play_bonuses.append(self.marker)
            if self.last:
                self.board.draw_bonuses.remove(self.last)
            if self.last:
                self.board.play_bonuses.remove(self.last)
            self.last = self.marker

        if self.tag == 'e_poorbonus' and all([len(self.board.curr_keep) < len(keep)
                                              for keep in self.board.keeps
                                              if keep.player_num != self.board.active_player]):
            self.board.draw_bonuses.append(self.marker)
            if self.last:
                self.board.draw_bonuses.remove(self.last)
            self.last = self.marker

        if self.tag == 'e_richbonus' and all([len(self.board.curr_keep) > len(keep)
                                              for keep in self.board.keeps
                                              if keep.player_num != self.board.active_player]):
            self.board.play_bonuses.append(self.marker)
            if self.last:
                self.board.play_bonuses.remove(self.last)
            self.last = self.marker

        if self.tag in {'e_inflation', 'e_doubleagenda'}:
            pass


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
        pass

    def repeal(self):
        pass

    def rule(self):
        pass

    def start(self):
        if self.tag == 's_nohandbonus':
            self.board.curr_hand.draw(self.size)
        if self.tag == 's_firstplayrandom' and self.board.play_state > 1:
            pick = choice(list(self.board.curr_hand))
            pick.play()


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
        hand = self.board.curr_hand
        keep = self.board.curr_keep
        self.used = True
        self.last_used = self.board.player_state
        if self.tag == 'fa_swapplaysfordraws':
            hand.draw(self.board.play_state - self.board.cards_played)
            for _ in range(self.board.play_state - self.board.cards_played):
                self.board.inc_cards_played()
        if self.tag == 'fa_mysteryplay':
            mcard = self.board.deck.draw()
            mcard.play()
            self.board.mysteryplay = mcard
        if self.tag == 'fa_goalmill':
            self.board.action_type = 'goalmill'
            if len(self.board.options) == 0:
                raise Board.IllegalMove('You have no goals.')
        if self.tag == 'fa_getonwithit':
            if len(hand) > 0:
                for card in hand:
                    hand.discard(card)
                hand.draw(3)
            else:
                raise Board.IllegalMove(self, 'You cannot use Get On With It! with an empty hand.')
        if self.tag == 'fa_recycling':
            if len(keep) > 0:
                self.board.action_type = 'recycling'
            else:
                raise Board.IllegalMove(self, 'You cannot use Recycling with an empty keep.')


class Action(Card):
    def __init__(self, board, name, tag):
        super(Action, self).__init__(board, name)
        self.tag = tag
        self._size = None
        if tag in {'a_draw3play2', 'a_jackpot', 'a_draw2use2', 'a_tax', 'a_everybody1'}:
            self.numeral = 0
        if tag in {'a_draw3play2', 'a_jackpot'}:
            self._size = 3
        elif tag in {'a_draw2use2'}:
            self._size = 2
        elif tag in {'a_tax', 'a_everybody1'}:
            self._size = 1
        self.used = None

    @property
    def size(self):
        if self._size:
            return self._size + self.numeral
        else:
            raise TypeError(f'Card {self.name} does not have a size.')

    def trash(self):
        raise Board.IllegalMove(self.board, f"Tried to trash an Action Card, it shouldn't have ever "
                                f"been permanent. Card Name: {self.name}")

    def a_draw3play2(self):
        self.board.temphands.append(Hand.temphand(self.size, self.board))
        self.board.action_type = 'play2'

    def a_draw2use2(self):
        self.board.temphands.append(Hand.temphand(self.size, self.board))
        self.board.action_type = 'play2'

    def a_jackpot(self):
        hand = self.board.curr_hand
        hand.draw(3)

    def a_tax(self):
        hand = self.board.curr_hand
        for o_hand in (h for i, h in enumerate(self.board.hands) if i != self.board.player_state):
            pick = choice(list(o_hand))
            hand.add(pick)
            o_hand.cards.discard(pick)

    def a_everybody1(self):
        self.board.temphands.append(Hand.temphand(self.size * self.board.num_players, self.board))
        self.board.action_type = 'everybody1'
        
    def a_anotherturn(self):
        self.used = True
        self.board.free_turn = True
    
    def a_discardanddraw(self):
        hand = self.board.curr_hand
        n_cards = len(hand) - 1
        temp = []
        for card in hand:
            temp.append(card)
        for card in temp:
            card.trash_from_hand()
        hand.draw(n_cards)

    def a_sharethewealth(self):
        held_keepers = []
        for keep in self.board.keeps:
            for keeper in keep:
                held_keepers.append(keeper)
        for keeper in held_keepers:
            keeper.discard_from_keep()
        shuffle(held_keepers)
        playerlist = cycle(range(self.board.num_players))
        for _ in range(self.board.player_state):
            next(playerlist)
        for keeper in held_keepers:
            tar_player = next(playerlist)
            self.board.keeps[tar_player].add(keeper)

    def a_zap(self):
        self.board.action_type = 'zap'

    def a_rotatehands(self):
        self.board.action_type = 'rotate'

    def a_dothatagain(self):
        self.board.action_type = 'doitagain'
        if len(self.board.options) == 0:
            self.board.action_type = 'normal'
            raise Board.IllegalPlay(self.board, 'There are no Actions or New Rules to play.')

    def a_steal(self):
        self.board.action_type = 'steal'
        if len(self.board.options) == 0:
            self.board.action_type = 'normal'
            raise Board.IllegalPlay(self.board, 'There are no Keepers to steal.')

    def a_simplify(self):
        self.board.action_type = 'simplify'

    def a_trash(self):
        self.board.action_type = 'trash'

    def a_exchange(self):
        self.board.action_type = 'exchange1'

    def a_trade(self):
        self.board.action_type = 'trade'

    def a_rulesreset(self):
        temp = []
        for card in self.board.rules:
            temp.append(card)
        for card in temp:
            card.trash()

    def a_usetake(self):
        self.board.action_type = 'usetake'

    def a_nolimits(self):
        temp = []
        for card in [rule for rule in self.board.rules if isinstance(rule, Limit)]:
            temp.append(card)
        for card in temp:
            card.trash()

    def a_emptytrash(self):
        new_trash = Deck.discard_creator(self.board)
        new_trash.append(self)
        beep = []
        for card in self.board.trash:
            self.board.deck.append(card)
            beep.append(card)
        for card in beep:
            self.board.trash.remove(card)
        shuffle(self.board.deck)

    def do(self):
        type(self).__dict__[self.tag](self)
        self.board.trash.append(self)
