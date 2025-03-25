from table import Table
from player import Player
from deck import Deck


def pretty_print(state):
    for k, v in state.items():
        if k == 'players':
            continue
        print(f'{k}:\t{v}')
    for d in state['players']:
        for k, v in d.items():
            if k != 'name':
                print(f'\t{k}:\t{v}')
            else:
                print(v)


# create table
t = Table(sb=1, bb=2)

# add players
t.add_player(Player('zamazer', 100, t))
t.add_player(Player('labazer', 200, t))

# print('table state for zamazer:')

# round
t.new_round()
r = t.current_round
a = t.players[0]
b = t.players[1]

pretty_print(t.state('zamazer'))
# preflop
b.bet(10)
a.call(r.max_bet)

# flop
a.check()
b.check()

# turn
a.check()
b.check()

a.check()
b.check()

