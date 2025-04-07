from pokergame.table import Table
from pokergame.player import Action
import uuid


games = {}


def pretty_print(data):
    print('table data:')
    for k, v in data.items():
        if k == 'players' or k == 'round':
            continue
        print(f'{k:>12}:\t{v:>12}')
    if 'round' in data:
        print('current round:')
        for k, v in data['round'].items():
            # if k != 'players': print(f'{k:>12}:\t{v:>12}')
            print(k, v)
    for d in data['players']:
        for k, v in d.items():
            if k != 'name' and k != 'cards':
                print(f'{k:>12}:\t{v:>12}')
            else:
                print(v)


def generate_id():
    # Generate unique ID for the game
    game_id = str(uuid.uuid4())[:8]
    if game_id in games:
        return generate_id()
    return game_id


# create table
t = Table(generate_id(), sb=1, bb=2)
print("table created")


# add/remove players
t.add_player(1, 'zamazer', 100)
t.add_player(2, 'labazer', 200)

t.remove_player('labazer')

t.add_player(3, 'mamaz', 1500)
# pretty_print(t.data())

# start game
t.start_game()
print('game started')

# pretty_print(t.data())

print('private datas:')
for player_name in ['zamazer', 'mamaz']:
    print('player name:', player_name)
    print(t.private_data(player_name))

# Hand 1
# preflop
t.act(action=Action.CALL, player_name='mamaz', amount=1.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)

# flop
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)

# turn
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)

# river
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)

# Hand 2
print('Hand 2')
t.new_round()
print('private datas:')
for player_name in ['zamazer', 'mamaz']:
    print('player name:', player_name)
    print(t.private_data(player_name))
# preflop
t.act(action=Action.CALL, player_name='zamazer', amount=1.0)
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)

print(*t.players, sep='\n')

# flop
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)

# turn
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)

# river
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)

pretty_print(t.data())
