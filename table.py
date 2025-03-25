from deck import Deck


class Round:
    def __init__(self, players, table):
        # players in game (including all_in) sorted by left to act
        first = table.button + 1
        self.players = players[first:] + players[:first]
        assert len(players) >= 2, 'not enough players'

        self.table = table

        self.sb = table.sb
        self.bb = table.bb

        self.street = 'preflop'
        self.deck = Deck()
        self.pot = 0
        self.board = []

    # streets
    def preflop(self):
        self.street = 'preflop'
        # deal cards
        for p in self.players:
            cards = [self.deck.pop(), self.deck.pop()]
            p.deal(cards)
        n = len(self.players)

        # blinds
        if n == 2:
            sb = 1
            bb = 0
        else:
            sb = 0
            bb = 1

        for p in self.players:
            p.is_acting = False
            p.chips_bet = 0

        self.players[sb].is_acting = True
        self.players[sb].blind(self.sb)
        self.players[bb].blind(self.bb)

    def flop(self):
        self.street = 'flop'
        # deal flop
        flop_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        self.board = flop_cards

        n = len(self.players)
        for p in self.players:
            p.is_acting = False
            p.chips_bet = 0
        self.players[(self.button + 1) % n].is_acting = True

    def turn(self):
        self.street = 'turn'
        # deal flop
        turn_cards = [self.deck.pop()]
        self.board += turn_cards

        n = len(self.players)
        for p in self.players:
            p.is_acting = False
            p.chips_bet = 0
        self.players[(self.button + 1) % n].is_acting = True

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
            self.win([self.players[0]])
            return

        max_bet = max(self.players, key=lambda p: p.chips_bet)

        def to_act_f(p):
            return not p.all_in and not p.chips_bet == max_bet

        # check how many left to act
        to_act = list(filter(to_act_f, self.players))
        if len(to_act) == 0:
            self.flop()
            return

        # next to act
        for i, p in enumerate(to_act):
            if p.is_acting:
                p.is_acting = False
                next_p = to_act[(i + 1) % len(to_act)]
                next_p.is_acting = True
                break

    def next_street(self):
        if self.street == 'preflop':
            self.flop()
        elif self.street == 'flop':
            self.turn()
        elif self.street == 'turn':
            self.river()
        elif self.street == 'river':
            self.showdown()

    def win(self, player_names):
        winners = []  # TODO: manage situations with all_ins
        for p in self.players:
            if p in player_names:
                winners.append(p)
        assert len(winners) != 0, 'no winners'
        for w in winners:
            w.stack += self.pot / len(winners)

        print('winners:', winners)
        self.table.new_round()

    def state(self):
        in_game = [p.name for p in self.players]
        res = {'players': in_game,
               'street': self.street,
               'pot': self.pot}
        return res


class Table:
    def __init__(self, sb, bb):
        self.bb = bb
        self.sb = sb
        self.players = []
        self.button = 0  # button index

        self.current_round = None

    def add_player(self, player):
        self.players.append(player)

    def state(self, player_name):
        players = [p.state(show_cards=(player_name == p.name)) for p in self.players]
        res = {'players': players, 'button': self.button}
        if self.current_round:
            res['round'] = self.current_round.state()
        return res

    def new_round(self):
        self.button = (self.button + 1) % len(self.players)
        self.current_round = Round(self.players, self)
        self.current_round.preflop()

    def __repr__(self):
        return f'sb: {self.sb}\t bb: {self.bb}\nplayers: {self.players}'
