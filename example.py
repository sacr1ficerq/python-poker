from pokergame.table import Table
from pokergame.player import Action
import uuid


games = {}


def pretty_print(state):
    print('table state:')
    for k, v in state.items():
        if k == 'players' or k == 'round':
            continue
        print(f'{k:>12}:\t{v:>12}')
    if 'round' in state:
        print('current round:')
        for k, v in state['round'].items():
            if k != 'players': print(f'{k:>12}:\t{v:>12}')
    for d in state['players']:
        for k, v in d.items():
            if k != 'name':
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
# pretty_print(t.state())

# start game
t.start_game()
print('game started')

# pretty_print(t.state())

print('private states:')
for player_name in ['zamazer', 'mamaz']:
    print('player name:', player_name)
    print(t.private_state(player_name))

# preflop
pretty_print(t.state())
t.act(action=Action.RAISE, player_name='zamazer', amount=10.0)
pretty_print(t.state())
