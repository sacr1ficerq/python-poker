from enum import Enum


class Action(Enum):
    FOLD = 0,
    CHECK = 1,
    CALL = 2,
    BET = 3,
    RAISE = 4


class Player:
    def __init__(self, id,  name, stack, table):
        self.name = name
        self.stack = stack
        self.table = table

        self.sit_out = False

        self.folded = False
        self.all_in = False
        self.acted = False

        self.id = id

        self.chips_bet = 0

        self.cards = []

    def state(self):
        return {'id': self.id,
                'name': self.name,
                'stack': self.stack,
                'folded': self.folded,
                'all_in': self.all_in,
                'bet': self.chips_bet,
                }

    def private_state(self):
        return {'cards': self.cards}

    def __repr__(self):
        return f'player: \'{self.name}\'\tchips: {self.stack}'

    def deal(self, cards):
        assert len(cards) == 2
        self.folded = False
        self.is_acting = False

        self.cards = cards

    def act(self, action: Action, amount):
        max_bet = self.table.current_round.max_bet
        print(f'player: {self.name}\t action:{action}')
        match action:
            case Action.FOLD:
                self.fold(max_bet)
            case Action.CHECK:
                self.check(amount, max_bet)
            case Action.CALL:
                self.call(amount, max_bet)
            case Action.BET:
                self.bet(amount, max_bet)
            case Action.RAISE:
                self.raise_bet(amount, max_bet)

    def bet(self, amount, max_bet):
        assert not self.folded, 'player already folded'
        assert self.is_acting
        if amount >= self.stack:
            self.all_in = True
            amount = self.stack

        self.stack -= amount
        self.chips_bet += amount

        print(f'player {self.name} bets {amount}')
        self.acted = True
        self.table.current_round.action(amount)

    def raise_bet(self, amount, max_bet):
        assert max_bet != 0, 'cant raise while bet == 0'
        assert not self.folded, 'player already folded'
        if amount >= self.stack:
            self.all_in = True
            amount = self.stack

        self.stack -= amount + max_bet - self.chips_bet
        self.chips_bet += amount + max_bet - self.chips_bet

        print(f'player {self.name} raises {amount}')
        self.acted = True
        self.table.current_round.action(amount)

    def call(self, max_bet):
        assert max_bet != 0, 'cant call while bet == 0'
        assert not self.folded, 'player already folded'
        amount = max_bet - self.chips_bet
        if amount >= self.stack:
            self.all_in = True
            amount = self.stack

        self.stack -= amount
        self.chips_bet += amount

        print(f'player {self.name} calls {amount}')
        self.acted = True
        self.table.current_round.action(amount)

    def check(self, max_bet=0):
        assert max_bet == 0, 'cant check while bet != 0'
        assert not self.folded, 'player already folded'

        print(f'player {self.name} checks')
        self.acted = True
        self.table.current_round.action(0)

    def fold(self, max_bet=0):
        assert not self.folded, 'player already folded'

        self.folded = True
        print(f'player {self.name} folds')
        self.acted = True
        self.table.current_round.action(0)

    def blind(self, amount):
        assert not self.folded, 'player already folded'
        if amount >= self.stack:
            self.all_in = True
            amount = self.stack

        self.stack -= amount
        self.chips_bet += amount

        print(f'player {self.name} posts blind {amount}')
        self.table.current_round.action(amount)
