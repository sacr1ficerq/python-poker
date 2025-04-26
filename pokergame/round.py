from .evaluate import evaluate_hand
from .deck import Deck, Card, Holding
from .player import PlayerState, Player

from .states import RoundData, Street

from typing import List, Tuple

class Round:
    def __init__(self, players: List[Player], table, starting_pot: float):
        # players in game (including all_in) sorted by left to act
        first = 1 - table.button

        assert len(players) == 2, 'wrong amount of players'
        self.players: List[Player] = [players[first], players[1 - first]]

        print('new round')
        print('players:')
        print(*map(lambda p: p.name, self.players), sep='\n')
        for p in self.players:
            p.chips_bet = 0
            p.acted = False
            p.player_state = PlayerState.BASE

        self.table = table
        self.button: int = table.button

        self.sb: float = table.sb
        self.bb: float = table.bb

        self.street: Street = Street.PREFLOP
        self.deck: Deck = Deck()
        self.pot: float = 0
        self.max_bet: float = 0
        self.board: List[Card] = []

        self.round_ended: bool = False

        self.max_bet_amount: float = min(self.players[0].stack, self.players[0].stack)
        self.min_bet_amount: float = self.table.bb + self.sb  # preflop minraise

        self.starting_pot: float = starting_pot
        self.starting_board: List[Card] | None = None

        self.acting: int = 0  # index of player who is currently to act

    def preflop(self):
        # deal cards
        for p in self.players:
            # TODO: remove assymetry
            holding = self.deck.sample_hand(p.preflop_range)
            p.deal(holding)

        for p in self.players:
            p.chips_bet = 0
        self.pot = self.starting_pot
        self.next_street()

    def action(self, delta: float):
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
                flop_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
                print(f'flop: {flop_cards}')
                self.board += flop_cards
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
        
        players_cards: List[Tuple[str, str]] = [(str(p.holding.c1), str(p.holding.c2)) for p in self.players]

        board_cards = list(map(str, self.board))
        evals = evaluate_hand(board_cards, players_cards)

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
                if self.starting_board:
                    flop_cards = self.starting_board
                else:
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
        board_cards = list(map(str, self.board))
        return RoundData(self.street.value,
                         self.max_bet,
                         board_cards,
                         self.pot,
                         self.max_bet_amount,
                         self.min_bet_amount,
                         self.round_ended,
                         self.players[1].name)
