from .player import Player, Action
from .round import Round
from .states import TableData, Street
from .deck import Range

from typing import Dict, List

from dataclasses import asdict

class Table:
    def __init__(self, id: str, starting_pot: float, depth: float, move_button:bool, sb: float, bb: float):
        self.id = id

        assert sb <= bb, 'sb > bb'
        self.bb = bb
        self.sb = sb
        self.players: List[Player] = []

        self.button = 0  # button index
        self.move_button = move_button

        self.current_round: Round | None = None

        self.game_started: bool = False
        self.starting_pot: float = starting_pot
        self.depth: float = depth

        self.hands_played: int = 0

    def add_player(self, player: Player) -> None:
        self.game_started = False
        self.current_round = None
        self.players.append(player)

    def get_player(self, name: str) -> Player | None:
        for p in self.players:
            if p.name == name:
                return p
        return None

    def remove_player(self, name: str):
        self.game_started = False
        self.current_round = None

        p = self.get_player(name)
        if p is None:
            return
        self.players.remove(p)

    def state(self, show_cards: bool=False) -> TableData:
        round = None
        show_cards = False
        if self.current_round:
            show_cards = show_cards or self.current_round.street == Street.SHOWDOWN
            round = asdict(self.current_round.state())
        players = [asdict(p.state(show_cards)) for p in self.players]
        return TableData(players,
                         round,
                         self.depth,
                         self.starting_pot,
                         handsPlayed=self.hands_played)

    def data(self, show_cards: bool=False) -> dict:
        return asdict(self.state(show_cards))

    def private_state(self, player_name):
        p = self.get_player(player_name)
        assert p is not None, 'player not found'
        return p.state(show_cards=True)

    def private_data(self, player_name) -> dict:
        p = self.get_player(player_name)
        assert p is not None, 'player not found'
        return asdict(p.state(show_cards=True))

    def start_game(self) -> None:
        n = len(self.players)
        assert n == 2, 'wrong amount of players'
        assert self.players[0].preflop_range is not None
        assert self.players[1].preflop_range is not None

        self.new_round()
        self.game_started = True

    def new_round(self) -> None:
        assert self.current_round is None or self.current_round.round_ended, \
               'cant start new round while current round not emded'
        n = len(self.players)
        assert n == 2, 'wrong amount of players'

        if self.move_button and self.game_started:
            self.button = 1 - self.button
            self.players[0].preflop_range, self.players[1].preflop_range = self.players[1].preflop_range, self.players[0].preflop_range
        if self.game_started:
            self.hands_played += 1

        self.current_round = Round(self.players, self, self.starting_pot)
        self.current_round.preflop()

    def act(self, action: Action, player_name: str, amount: float) -> None:
        round = self.current_round
        assert isinstance(amount, float) or isinstance(amount, int)
        assert round is not None
        assert round.players[round.acting].name == player_name, f'its not {player_name} turn'
        p = self.get_player(player_name)
        assert p is not None, 'wrong player name'
        p.act(action=action, amount=amount)

    def __repr__(self) -> str:
        return f'sb: {self.sb}\t bb: {self.bb}\nplayers: {self.players}'
