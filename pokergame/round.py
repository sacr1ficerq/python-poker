from .evaluate import evaluate_hand
from .deck import Deck


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

        self.street = 'preflop'
        self.deck = Deck()
        self.pot = 0
        self.max_bet = 0
        self.board = []

        self.winners = []
        self.round_ended = False

        self.show_hands = False

        self.acting = 0  # index of player who is currently to act

    # streets
    def preflop(self):
        self.street = 'preflop'
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

    def flop(self):
        self.street = 'flop'
        # deal flop
        flop_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        print(f'flop: {flop_cards}')
        self.board = flop_cards

    def turn(self):
        self.street = 'turn'
        # deal turn
        turn_cards = [self.deck.pop()]
        print(f'turn: {turn_cards}')
        self.board += turn_cards

    def river(self):
        self.street = 'river'
        # deal river
        river_cards = [self.deck.pop()]
        print(f'river: {river_cards}')
        self.board += river_cards

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

    def action(self, delta):
        self.pot += delta
        """
        Called after player acted
        delta: pot-after-action - pot-before-action
        """

        def in_game_f(p):
            return not p.folded

        self.players = list(filter(in_game_f, self.players))
        assert len(self.players) != 0, 'no one playing'

        if len(self.players) == 1:
            self.win([self.players[0].name])
            return

        self.max_bet = max(self.players, key=lambda p: p.chips_bet).chips_bet

        def to_act_f(p):
            return not p.all_in and p.chips_bet != self.max_bet or not p.acted

        # check how many left to act
        to_act = list(filter(to_act_f, self.players))
        if len(to_act) == 0:
            self.next_street()
            return

        # next to act
        self.acting = (self.acting + 1) % 2

    def next_street(self):
        for p in self.players:
            p.chips_bet = 0
            p.acted = False
        self.max_bet = 0

        if self.street == 'preflop':
            self.flop()
        elif self.street == 'flop':
            self.turn()
        elif self.street == 'turn':
            self.river()
        elif self.street == 'river':
            self.showdown()

    def win(self, player_names):
        self.round_ended = True
        self.winners = []  # TODO: manage situations with all_ins
        for p in self.players:
            if p.name in player_names:
                self.winners.append(p)
        assert len(self.winners) != 0, 'no self.winners'
        for w in self.winners:
            w.stack += self.pot / len(self.winners)

        print('self.winners:', self.winners)

    def state(self):
        res = {}
        if self.round_ended:
            if self.show_hands or self.street == 'showdown':
                players = [p.private_state() for p in self.players]
            else:
                players = [p.name for p in self.players]
            res = {'players': players,
                   'winners': self.winners,
                   'street': self.street,
                   'board': self.board,
                   'pot': self.pot}
        else:
            players = [p.name for p in self.players]
            acting = self.players[self.acting].name
            res = {'players': players,
                   'street': self.street,
                   'max_bet': self.max_bet,
                   'acting': acting,
                   'board': self.board,
                   'pot': self.pot}
        return res
