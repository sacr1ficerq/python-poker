from .player import Player, Action
from .round import Round
from .states import TableData, Street


from dataclasses import asdict


class Table:
    def __init__(self, id, sb, bb):
        self.bb = bb
        self.sb = sb
        self.players = []
        self.button = 0  # button index

        self.id = id
        self.current_round = None

        self.game_started = False

    def add_player(self, id, name, stack):
        player = Player(id, name, stack, self)
        self.players.append(player)

    def remove_player(self, name):
        for p in self.players:
            if p.name == name:
                self.players.remove(p)

    def state(self, show_cards=False) -> TableData:
        if self.current_round:
            show_cards = show_cards or self.current_round.street == Street.SHOWDOWN
            players = [p.state(show_cards) for p in self.players]
            return TableData(players, self.current_round.state())
        else:
            players = [p.state() for p in self.players]
            return TableData(players, None)


    def data(self, show_cards=False) -> dict:
        if self.current_round:
            show_cards = show_cards or self.current_round.street == Street.SHOWDOWN
            players = [asdict(p.state(show_cards)) for p in self.players]
            but = self.players[self.button].name
            return {'players': players, 'button': but, 'round': asdict(self.current_round.state())}

        players = [asdict(p.state()) for p in self.players]
        but = self.players[self.button].name
        return {'players': players, 'button': but}

    def private_state(self, player_name):
        for p in self.players:
            if p.name == player_name:
                return p.state(show_cards=True)
        assert False, 'player not found'

    def private_data(self, player_name) -> dict:
        for p in self.players:
            if p.name == player_name:
                return asdict(p.state(show_cards=True))
        assert False, 'player not found'

    def start_game(self):
        n = len(self.players)
        assert n == 2, 'wrong amount of players'

        self.game_started = True
        self.new_round()

    def new_round(self):
        assert self.game_started
        n = len(self.players)
        assert n == 2, 'wrong amount of players'

        self.button = 1 - self.button
        self.current_round = Round(self.players, self)
        self.current_round.preflop()

    def act(self, action: Action, player_name: str, amount: float):
        round = self.current_round
        assert isinstance(amount, float) or isinstance(amount, int)
        assert round is not None
        assert round.players[round.acting].name == player_name, f'its not {player_name} turn'
        for p in self.players:
            if p.name == player_name:
                p.act(action=action, amount=amount)
                return
        assert False, 'wrong player name'

    def __repr__(self) -> str:
        return f'sb: {self.sb}\t bb: {self.bb}\nplayers: {self.players}'
