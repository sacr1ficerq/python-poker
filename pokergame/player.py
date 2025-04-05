from enum import Enum
from .round import Street


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
                'allIn': self.all_in,
                'bet': self.chips_bet,
                }

    def private_state(self):
        return {'name': self.name, 'cards': self.cards}

    def __repr__(self):
        res = [self.name, self.stack, self.folded, self.all_in, self.chips_bet]
        cols = ['name', 'stack', 'folded', 'all_in', 'chips_bet']
        return '\t'.join(cols) + '\n' + '\t'.join(map(str, res))

    def deal(self, cards):
        assert len(cards) == 2
        self.folded = False

        self.cards = cards

    def act(self, action: Action, amount=0.0):
        print(f'player: {self.name}\t action:{action} for {amount}')
        assert not self.folded, 'player already folded'
        assert not self.all_in, 'player already all_in'
        round = self.table.current_round

        self.acted = True
        assert amount <= round.max_bet_amount, 'wrong sizing'
        assert amount <= self.stack, 'cant bet more then stack'


        if amount == self.stack:
            self.all_in = True

        match action:
            case Action.FOLD:
                self.folded = True
            case Action.CHECK:
                assert round.max_bet == 0 \
                    or (round.street == Street.PREFLOP and self.chips_bet == round.max_bet), \
                    'cant check with bet != 0'
            case Action.CALL:
                assert round.max_bet != 0, 'cant call with max_bet == 0'
                assert amount + self.chips_bet == round.max_bet, \
                    f'wrong amount, correct amount: {round.max_bet - self.chips_bet}'
            case Action.BET:
                assert round.max_bet == 0, 'cant bet with max_bet != 0'
                assert amount >= round.min_bet_amount
            case Action.RAISE:
                assert round.max_bet != 0
                assert amount >= round.min_bet_amount

        self.stack -= amount
        self.chips_bet += amount

        self.table.current_round.action(amount)

    def blind(self, amount):
        print(f'player {self.name} posts blind {amount}')

        assert not self.folded, 'player already folded'
        assert not self.all_in, 'player already all_in'

        assert amount < self.stack, 'dont have enough for blind'

        self.stack -= amount
        self.chips_bet += amount
