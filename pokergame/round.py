from .evaluate import evaluate_hand
from .deck import Deck
from .player import PlayerState

from .states import RoundData, Street


class Round:
    def __init__(self, players, table):
        # players in game (including all_in) sorted by left to act
        first = 1 - table.button

        assert len(players) == 2, 'wrong amount of players'
        self.players = [players[first], players[1 - first]]

        print('new round')
        print('players:')
        print(*map(lambda p: p.name, self.players), sep='\n')
        for p in self.players:
            p.chips_bet = 0
            p.acted = False
            p.player_state = PlayerState.BASE

        self.table = table
        self.button = table.button

        self.sb = table.sb
        self.bb = table.bb

        self.street = Street.PREFLOP
        self.deck = Deck()
        self.pot = 0
        self.max_bet = 0
        self.board = []

        self.round_ended = False

        self.max_bet_amount = min(self.players[0].stack, self.players[0].stack)
        self.min_bet_amount = self.table.bb + self.sb  # preflop minraise

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
        self.players[sb].player_state = PlayerState.ACTING

        self.players[sb].blind(self.sb)
        self.players[bb].blind(self.bb)
        self.max_bet = self.bb
        self.pot = self.sb + self.bb
        self.min_bet_amount = self.sb + self.bb

    def action(self, delta):
        """
        Called after player acted
        delta: fresh chips put into the pot
        """
        villain = self.players[self.acting]  # just acted

        self.acting = 1 - self.acting
        hero = self.players[self.acting]
        hero.player_state = PlayerState.ACTING

        assert delta >= 0
        if delta != 0:
            step = villain.chips_bet - hero.chips_bet
            self.min_bet_amount = max(self.table.bb, step * 2)  # raise step
            self.max_bet_amount = villain.stack + step  # max new delta
            self.min_bet_amount = min(self.min_bet_amount, self.max_bet_amount)

        self.pot += delta
        self.max_bet = villain.chips_bet

        if villain.player_state == PlayerState.FOLDED:
            self.win([hero])
            return

        if hero.chips_bet != villain.chips_bet:
            return  # waiting for hero move

        # bets equalized
        if (hero.is_all_in() or villain.is_all_in()):
            self.run()

        if hero.acted and villain.acted:
            # everyone acted and bets equalized
            self.next_street()

    def next_street(self):
        for p in self.players:
            p.chips_bet = 0
            p.acted = False
            p.player_state = PlayerState.BASE

        self.max_bet = 0
        self.acting = 0
        self.players[self.acting].player_state = PlayerState.ACTING

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
                return  # wait for next round start

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
            winners.append(self.players[p[1]])

        self.win(winners)

    def win(self, winners):
        self.round_ended = True
        for w in winners:
            chips_won = self.pot / len(winners)
            w.stack += chips_won
            w.player_state = PlayerState.WINNING
            print(f'{w.name} wins {chips_won}')

        print('winners:', winners)

    def state(self) -> RoundData:
        return RoundData(self.street.value,
                         self.max_bet,
                         self.board,
                         self.pot,
                         self.max_bet_amount,
                         self.min_bet_amount,
                         self.round_ended,
                         self.players[1].name)
