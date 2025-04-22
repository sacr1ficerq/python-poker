from .states import PlayerData, PlayerState, Action
from .deck import Holding, Range


class Player:
    def __init__(self, id: str,  name: str, stack: float, rng: Range, table):
        self.id = id
        self.name = name

        self.stack: float = stack
        self.table = table

        self.acted: bool = False
        self.player_state: PlayerState = PlayerState.BASE
    
        self.preflop_range: Range = rng
        self.holding: Holding | None = None
        self.chips_bet: float = 0

    def state(self, show_cards: bool=False) -> PlayerData:
        if show_cards:
            assert self.holding is not None, 'cards not dealt'
            return PlayerData(self.name,
                              self.stack,
                              self.player_state.value,
                              self.chips_bet,
                              str(self.holding))
        return PlayerData(self.name,
                          self.stack,
                          self.player_state.value,
                          self.chips_bet)

    def is_all_in(self):
        return self.player_state == PlayerState.ALLIN

    def __repr__(self):
        return '\t'.join([f'player: {self.name}',
                         f'stack: {self.stack}',
                         f'state: {self.player_state.value}'])

    def deal(self, holding: Holding):
        self.holding = holding

    def act(self, action: Action, amount=0.0):
        print(f'player: {self.name}\t action:{action.value} {amount}')
        assert self.player_state == PlayerState.ACTING, \
            f'cant {action.value} while {self.player_state}'
        round = self.table.current_round

        self.acted = True
        self.player_state = PlayerState.BASE
        assert amount <= round.max_bet_amount, 'wrong sizing'
        assert amount <= self.stack, 'cant bet more then stack'

        if amount == self.stack:
            self.all_in = True
            self.player_state = PlayerState.ALLIN

        match action:
            case Action.FOLD:
                self.player_state = PlayerState.FOLDED
            case Action.CHECK:
                assert self.chips_bet == round.max_bet, \
                    'cant check with uncalled bet'
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

    def blind(self, amount: float):
        print(f'player {self.name} posts blind {amount}')
        assert amount != self.stack, 'use all-in for that'
        assert amount < self.stack, 'dont have enough for blind'

        self.stack -= amount
        self.chips_bet += amount
