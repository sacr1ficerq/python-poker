from .evaluate import evaluate_hand, equity
from .deck import Deck, Card, Holding
from .player import PlayerState, Player

from .states import RoundData, Street

import numpy as np
from typing import List, Tuple

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

class Round:
    def __init__(self, players: List[Player], table, starting_pot: float):
        # players in game (including all_in) sorted by left to act
        first = 1 - table.button

        assert len(players) == 2, 'wrong amount of players'
        self.players: List[Player] = [players[first], players[1 - first]]

        logger.info('New round')
        logger.debug('Players: %s', '\n'.join(map(lambda p: p.name, self.players)))

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
        self.min_bet_amount: float = self.bb

        self.starting_pot: float = starting_pot
        self.starting_board: List[Card] | None = None

        self.acting: int = 0  # index of player who is currently to act

    def preflop(self):
        # deal cards
        first = np.random.randint(0, 1)
        
        holding = self.deck.sample_hand(self.players[first].preflop_range)
        self.players[first].deal(holding)

        holding = self.deck.sample_hand(self.players[1 - first].preflop_range)
        self.players[1 - first].deal(holding)

        self.min_bet_amount = self.table.bb + self.sb  # preflop minraise

        for p in self.players:
            p.chips_bet = 0
            p.last_action = '' # TODO: set to last preflop action
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
            logger.info(f'{hero.name} acting')

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

    def next_street(self) -> None:
        for p in self.players:
            p.chips_bet = 0
            p.acted = False
            p.player_state = PlayerState.BASE
            logger.debug(f'{p.name} chilling')
        
        self.min_bet_amount = self.bb
        self.max_bet_amount = min(self.players, key=lambda x: x.stack).stack

        self.max_bet = 0
        self.acting = 0
        self.players[self.acting].player_state = PlayerState.ACTING
        self.players[self.acting].last_action = ''
        logger.info(f'{self.players[self.acting].name} acting')

        match self.street:
            case Street.PREFLOP:
                self.street = Street.FLOP
                flop_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
                logger.info(f'flop: {flop_cards}')
                self.board += flop_cards
            case Street.FLOP:
                self.street = Street.TURN
                turn_cards = [self.deck.pop()]
                logger.info(f'turn: {turn_cards}')
                self.board += turn_cards
            case Street.TURN:
                self.street = Street.RIVER
                river_cards = [self.deck.pop()]
                logger.info(f'river: {river_cards}')
                self.board += river_cards
            case Street.RIVER:
                self.street = Street.SHOWDOWN
                self.showdown()
            case Street.SHOWDOWN:
                return  # wait for next round start

    def showdown(self):
        logger.info('Showdown')
        logger.info('Board: %s', self.board)
        
        assert all(list(map(lambda p: p.holding is not None, self.players)))
        players_cards: List[Tuple[str, str]] = [(str(p.holding.c1), str(p.holding.c2)) for p in self.players] # type: ignore
        
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
        self.max_bet = 0
        for p in self.players:
            p.chips_bet = 0
        if self.street == Street.RIVER:
            self.street = Street.SHOWDOWN
            return self.showdown()

        hero, villain = self.players
        hero_state = hero.player_state.value
        villain_state = villain.player_state.value
        assert 'all-in' in [hero_state, villain_state], \
            'no one is all-in ' + hero_state + ' ' + villain_state

        if self.street == Street.SHOWDOWN:
            return
        assert hero.holding is not None and villain.holding is not None
        eq: float = round(equity(self.deck, hero.holding, villain.holding, self.board) * 100, 2)
        hero.last_action = f'{eq}%'
        villain.last_action = f'{100 - eq}%'
        
        chips_won = round(eq/100 * self.pot, 2)
        hero.stack += chips_won
        villain.stack += self.pot - chips_won
        
        self.round_ended = True
        self.street = Street.SHOWDOWN

        t = self.table

        profit = hero.stack - t.depth - t.starting_pot / 2
        hero.profit += profit;
        hero.stack = t.depth
        
        villain.profit -= profit
        villain.stack = t.depth


    def win(self, winners):
        self.round_ended = True
        for p in self.players:
            p.player_state = PlayerState.LOOSING
        for w in winners:
            chips_won = self.pot / len(winners)
            w.stack += chips_won
            w.player_state = PlayerState.WINNING
            logger.info(f'{w.name} wins {chips_won}')

        t = self.table
        for p in t.players:
            profit = p.stack - t.depth - t.starting_pot / 2
            p.profit += profit;
            p.stack = t.depth

        logger.info('winners: %s', winners)
        logger.info('loosers: %s', list(filter(lambda p: p.player_state == PlayerState.LOOSING, self.players)))
        logger.debug('players: %s', [p.state() for p in self.players])

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
