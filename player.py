class Player:
    def __init__(self, name, stack, table):
        self.name = name
        self.stack = stack
        self.table = table

        self.sit_out = False

        self.folded = False
        self.all_in = False
        self.is_acting = False

        self.chips_bet = 0

        self.cards = []

    def state(self, show_cards=False):
        return {'name': self.name,
                'stack': self.stack,
                'folded': self.folded,
                'all_in': self.all_in,
                'is_acting': self.is_acting,
                'bet': self.chips_bet,
                'cards': self.cards if show_cards else []
                }

    def __repr__(self):
        return f'player: \'{self.name}\'\tchips: {self.stack}'

    def deal(self, cards):
        assert len(cards) == 2
        self.folded = False
        self.is_acting = False

        self.cards = cards

    def bet(self, amount):
        assert not self.folded, 'player already folded'
        assert self.is_acting
        if amount >= self.stack:
            self.all_in = True
            amount = self.stack

        self.stack -= amount
        self.chips_bet += amount

        self.table.current_round.action(amount)

    def check(self):
        assert not self.folded, 'player already folded'
        assert self.is_acting

        self.table.current_round.action(0)

    def fold(self):
        assert not self.folded, 'player already folded'
        assert self.is_acting

        self.folded = True
        self.table.current_round.action(0)

    def blind(self, amount):
        assert not self.folded, 'player already folded'
        if amount >= self.stack:
            self.all_in = True
            amount = self.stack

        self.stack -= amount
        self.chips_bet += amount

        self.table.current_round.action(amount)
