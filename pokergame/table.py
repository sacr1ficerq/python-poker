from .player import Player, Action
from .round import Round
from .states import TableData, Street
from .deck import Range

from typing import Dict

from dataclasses import asdict

class Table:
    def __init__(self, id: str, starting_pot: float, depth: float, sb: float, bb: float):
        self.id = id

        assert sb <= bb, 'sb > bb'
        self.bb = bb
        self.sb = sb
        self.players = []
        self.button = 0  # button index

        self.current_round: Round | None = None

        self.game_started: bool = False
        self.starting_pot: float = starting_pot;
        self.depth: float = depth;

    def add_player(self, id, name: str, stack: float, preflop_range: Range):
        self.game_started = False
        self.current_round = None

        player = Player(id, name, stack, preflop_range, self)
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
        if self.current_round:
            show_cards = show_cards or self.current_round.street == Street.SHOWDOWN
            players = [p.state(show_cards) for p in self.players]
            return TableData(players, self.current_round.state(), self.depth, self.starting_pot)
        else:
            players = [p.state() for p in self.players]
            return TableData(players, None, self.depth, self.starting_pot)

    def data(self, show_cards: bool=False) -> dict:
        if self.current_round:
            show_cards = show_cards or self.current_round.street == Street.SHOWDOWN
            players = [asdict(p.state(show_cards)) for p in self.players]
            but = self.players[self.button].name
            return {'players': players, 'button': but, 'round': asdict(self.current_round.state())}

        players = [asdict(p.state()) for p in self.players]
        but = self.players[self.button].name
        return {'players': players, 'button': but}

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

        self.game_started = True
        self.new_round()

    def new_round(self) -> None:
        assert self.game_started
        assert self.current_round is None or self.current_round.round_ended, \
               'cant start new round while current round not emded'
        n = len(self.players)
        assert n == 2, 'wrong amount of players'


        self.button = 1 - self.button
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
