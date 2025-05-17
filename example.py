from pokergame.table import Table
from pokergame.player import Action, Player
from pokergame import Range, Holding
import uuid


games = {}

def generate_id():
    # Generate unique ID for the game
    game_id = str(uuid.uuid4())[:8]
    if game_id in games:
        return generate_id()
    return game_id


# create table
t = Table(generate_id(),starting_pot=5, depth=97.5, move_button=True, sb=1, bb=2)
print("table created")

# add/remove players
r1 = Range()
r1.set_holding(Holding(s='AcAh'), 0.8)
r1.set_holding(Holding(s='JsAc'), 0.2)

r2 = Range()
r2.set_holding(Holding(s='KcKh'), 0.8)
r2.set_holding(Holding(s='QsKc'), 0.2)

p2 = Player('1', 'mamaz', 100, r2, t, 0)
p1 = Player('0', 'zamazer', 100, r1, t, 0)

t.add_player(p2)
t.add_player(p1)

# start game
t.start_game()
print('game started')

print('private datas:')
for player_name in ['zamazer', 'mamaz']:
    print('player name:', player_name)
    print(t.private_data(player_name))

# Hand 1
# preflop

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

# preflop (there is no preflop)

# flop
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)

# turn
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)

# river
t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
