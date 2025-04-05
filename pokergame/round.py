from .evaluate import evaluate_hand
from .deck import Deck

from enum import Enum


class Street(Enum):
    PREFLOP = 'prefop'
    FLOP = 'flop'
    TURN = 'turn'
    RIVER = 'river'
    SHOWDOWN = 'showdown'


class Round:
    def __init__(self, players, table):
        # players in game (including all_in) sorted by left to act
        first = (table.button + 1) % 2

        assert len(players) == 2, 'wrong amount of players'
        self.players = [players[first], players[1 - first]]

        print('new round')
        print('players:')
        print(*map(lambda p: p.name, self.players), sep='\n')

        self.table = table

        self.sb = table.sb
        self.bb = table.bb

        self.street = Street.PREFLOP
        self.deck = Deck()
        self.pot = 0
        self.max_bet = 0
        self.board = []

        self.winners = []
        self.round_ended = False

        self.max_bet_amount = min(self.players[0].stack, self.players[0].stack)
        self.min_bet_amount = self.table.bb + self.sb  # preflop minraise

        self.show_hands = False

        self.acting = 0  # index of player who is currently to act

    def preflop(self):
        self.street = Street.PREFLOP
        # deal cards
        for p in self.players:
            cards = [self.deck.pop(), self.deck.pop()]
            p.deal(cards)

        # blinds
        sb = 1  # button
        bb = 0

        for p in self.players:
            p.chips_bet = 0

        self.acting = sb
        self.players[sb].blind(self.sb)
        self.players[bb].blind(self.bb)
        self.max_bet = self.bb
        self.pot += self.sb + self.bb
        self.min_bet_amount = self.sb + self.bb

    def action(self, delta):
        """
        Called after player acted
        delta: fresh chips put in pot
        """
        villain = self.players[self.acting]
        hero = self.players[1 - self.acting]  # now acting

        assert delta >= 0
        if delta != 0:
            # assert delta >= self.min_bet_amount\
            #   or self.players[self.acting].all_in, \
            #    'wrong sizing'
            step = villain.chips_bet - hero.chips_bet
            self.min_bet_amount = max(self.table.bb, step * 2)  # raise step
            self.max_bet_amount = villain.stack + step  # max new delta
            self.min_bet_amount = min(self.min_bet_amount, self.max_bet_amount)

        self.pot += delta
        self.max_bet = villain.chips_bet

        if villain.folded:
            self.win([hero.name])
            return

        self.acting = 1 - self.acting

        if (villain.acted or villain.all_in) and \
           (hero.acted or hero.all_in) and \
           (hero.chips_bet == villain.chips_bet):
            # everyone acted or all in, and bets equalized
            self.next_street()

    def next_street(self):
        villain = self.players[1 - self.acting]
        hero = self.players[self.acting]  # now acting

        hero.chips_bet = 0
        hero.acted = False

        villain.chips_bet = 0
        villain.acted = False

        self.max_bet = 0
        self.acting = 0

        match self.street:
            case Street.PREFLOP:
                self.street = Street.FLOP
                flop_cards = [self.deck.pop(),
                              self.deck.pop(),
                              self.deck.pop()]
                print(f'flop: {flop_cards}')
                self.board = flop_cards
            case Street.FLOP:
                self.street = Street.TURN
                turn_cards = [self.deck.pop()]
                print(f'turn: {turn_cards}')
                self.board += turn_cards
            case Street.TURN:
                self.street = Street.RIVER
                river_cards = [self.deck.pop()]
                print(f'river: {river_cards}')
                self.board += river_cards
            case Street.RIVER:
                self.street = Street.SHOWDOWN
                self.showdown()
            case Street.SHOWDOWN:
                return  # wait for next round
        if hero.all_in or villain.all_in:
            self.next_street()

    def showdown(self):
        print('showdown:')
        print('board:', self.board)

        players_cards = [p.cards for p in self.players]
        evals = evaluate_hand(self.board, players_cards)

        def rank(pair):
            return (pair[0]['rank'], pair[0]['combination'])

        pairs = sorted(zip(evals, range(len(self.players))),
                       key=rank,
                       reverse=True)
        winners = []
        for p in pairs:
            if p[0]['combination'] != pairs[0][0]['combination']:
                break
            winners.append(self.players[p[1]].name)

        print(*evals, sep='\n')
        print('winners:', winners)

        self.win(winners)

    def win(self, player_names):
        print(f'{player_names} won')
        self.round_ended = True
        self.winners = []  # TODO: manage situations with all_ins
        for p in self.players:
            if p.name in player_names:
                self.winners.append(p)
        assert len(self.winners) != 0, 'no self.winners'
        for w in self.winners:
            w.stack += self.pot / len(self.winners)
            print(f'{w.name} wins {self.pot / len(self.winners)}')

        print('self.winners:', self.winners)

    def state(self):
        res = {}
        if self.round_ended:
            if self.show_hands or self.street == Street.SHOWDOWN:
                players = [p.private_state() for p in self.players]
            else:
                players = [p.name for p in self.players]
            winners = [w.name for w in self.winners]
            res = {'players': players,
                   'winners': winners,
                   'street': self.street.value,
                   'board': self.board,
                   'pot': self.pot,
                   'roundEnded': 1}
        else:
            players = [p.name for p in self.players]
            acting = self.players[self.acting].name
            res = {'players': players,
                   'street': self.street.value,
                   'maxBet': self.max_bet,
                   'acting': acting,
                   'board': self.board,
                   'pot': self.pot,
                   'maxBetAmount': self.max_bet_amount,
                   'minBetAmount': self.min_bet_amount,
                   'roundEnded': 0}
        return res
