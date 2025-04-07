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

        sb_player = self.players[sb]
        bb_player = self.players[bb]
        max_bet = min(sb_player.stack, bb_player.stack)

        # DON'T REFACTOR THIS MESS UNTIL MVP READY
        if max_bet <= self.bb:
            if max_bet <= self.sb:
                # basicaly both all in for effective stack
                sb_player.stack -= max_bet
                sb_player.chips_bet += max_bet
                self.pot += max_bet
                if sb_player.stack == 0:
                    sb_player.player_state = PlayerState.ALLIN

                bb_player.stack -= max_bet
                bb_player.chips_bet += max_bet
                self.pot += max_bet
                self.max_bet = max_bet
                if bb_player.stack == 0:
                    bb_player.player_state = PlayerState.ALLIN
                self.run()
            else:
                # self.sb < max_bet <= self.bb
                # bb all_in for effective stack, sb has desicion
                sb_player.stack -= self.sb
                sb_player.chips_bet += self.sb
                self.pot += self.sb
                sb_player.player_state = PlayerState.ACTING
                self.acting = sb

                bb_player.stack -= max_bet
                bb_player.chips_bet += max_bet
                self.pot += max_bet
                self.max_bet = max_bet

                if bb_player.stack == 0:
                    bb_player.player_state = PlayerState.ALLIN
                self.max_bet_amount = max_bet - self.sb
                self.min_bet_amount = max_bet - self.sb
            return

        self.acting = sb
        self.players[sb].player_state = PlayerState.ACTING

        self.players[sb].blind(self.sb)
        self.players[bb].blind(self.bb)
        self.max_bet = self.bb
        self.pot = self.sb + self.bb
        self.min_bet_amount = self.sb + self.bb
        self.max_bet_amount = min(self.players[sb].stack, self.players[bb].stack + self.sb)

    def action(self, delta):
        """
        Called after player acted
        delta: fresh chips put into the pot
        """
        villain = self.players[self.acting]  # just acted
        self.acting = 1 - self.acting
        hero = self.players[self.acting]

        self.pot += delta
        self.max_bet = villain.chips_bet

        if (hero.is_all_in() and villain.is_all_in()):
            return self.run()

        if not hero.is_all_in():
            hero.player_state = PlayerState.ACTING
            print(f'{hero.name} acting')

        assert delta >= 0
        if delta != 0:
            step = villain.chips_bet - hero.chips_bet
            self.min_bet_amount = max(self.table.bb, step * 2)  # raise step
            self.max_bet_amount = villain.stack + step  # max new delta
            self.min_bet_amount = min(self.min_bet_amount, self.max_bet_amount)

        if villain.player_state == PlayerState.FOLDED:
            self.win([hero])
            return

        if hero.chips_bet != villain.chips_bet:
            return  # waiting for hero move

        # bets equalized
        if (hero.is_all_in() or villain.is_all_in()):
            return self.run()

        if hero.acted and villain.acted:
            # everyone acted and bets equalized
            self.next_street()

    def next_street(self):
        for p in self.players:
            p.chips_bet = 0
            p.acted = False
            p.player_state = PlayerState.BASE
            print(f'{p.name} chilling')

        self.max_bet = 0
        self.acting = 0
        self.players[self.acting].player_state = PlayerState.ACTING
        print(f'{self.players[self.acting].name} acting')

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

    def run(self):
        for p in self.players:
            p.chips_bet = 0
        hero_state = self.players[0].player_state.value
        villain_state = self.players[1].player_state.value
        assert 'all-in' in [hero_state, villain_state], \
            'no one is all-in ' + hero_state + ' ' + villain_state

        self.max_bet = 0

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
                return self.showdown()
            case Street.SHOWDOWN:
                return  # wait for next round start
        self.run()

    def win(self, winners):
        self.round_ended = True
        for p in self.players:
            p.player_state = PlayerState.LOOSING
        for w in winners:
            chips_won = self.pot / len(winners)
            w.stack += chips_won
            w.player_state = PlayerState.WINNING
            print(f'{w.name} wins {chips_won}')

        print('winners:', winners)
        print('loosers:', list(filter(lambda p: p.player_state == PlayerState.LOOSING, self.players)))
        print('players: ', [p.state() for p in self.players])

    def state(self) -> RoundData:
        return RoundData(self.street.value,
                         self.max_bet,
                         self.board,
                         self.pot,
                         self.max_bet_amount,
                         self.min_bet_amount,
                         self.round_ended,
                         self.players[1].name)
