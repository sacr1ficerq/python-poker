from pokergame.table import Table
from pokergame.player import Action
from pokergame.deck import Range, Holding

import pytest

SB = 0.5
BB = 1
DEPTH = 100
STARTING_POT = BB * 2.5 * 2

@pytest.fixture
def range_sb() -> Range:
    rng = Range()
    rng.set_holding(Holding(s='AcAh'), 0.8)     
    rng.set_holding(Holding(s='JcAc'), 0.2)     
    return rng

@pytest.fixture
def range_bb() -> Range:
    rng = Range()
    rng.set_holding(Holding(s='KcKh'), 0.8)     
    rng.set_holding(Holding(s='QcQc'), 0.2)     
    rng.set_holding(Holding(s='JcJc'), 0.2)     
    return rng

@pytest.fixture
def table(range_sb, range_bb):
    table = Table('test_table', SB, BB)
    table.add_player(0, 'BB', DEPTH, range_bb)
    table.add_player(1, 'BUT', DEPTH, range_sb)
    table.start_game(STARTING_POT)
    return table

@pytest.fixture
def players(t):
    return {p.name: p for p in t.players}

def test_start_game(range_sb, range_bb):
    # add/remove players
    table = Table('test_table', SB, BB)
    table.add_player(0, 'BB', DEPTH, range_bb)
    table.add_player(1, 'BUT', DEPTH, range_sb)
    table.start_game(STARTING_POT)

# def test_checkdown_1():
#     # create table
#     t = Table('', sb=1, bb=2)
# 
#     # add/remove players
#     t.add_player(1, 'zamazer', 100)
#     t.add_player(2, 'mamaz', 200)
#     # pretty_print(t.state())
# 
#     # start game
#     t.start_game()
# 
#     # Hand 1
#     # preflop
#     t.act(action=Action.CALL, player_name='mamaz', amount=1.0)
#     t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
# 
#     # flop
#     t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
#     t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
# 
#     # turn
#     t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
#     t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
# 
#     # river
#     t.act(action=Action.CHECK, player_name='zamazer', amount=0.0)
#     t.act(action=Action.CHECK, player_name='mamaz', amount=0.0)
# 
# 
# def test_checkdown_2():
#     t = Table('', sb=1, bb=2)
#     t.add_player(1, 'a', 100)
#     t.add_player(2, 'b', 100)
#     # start game
#     t.start_game()
#     print(t.current_round.players)  # a, b
# 
#     # b is dealer
#     # Hand 1
#     # preflop
#     t.act(Action.CALL, 'b', 1.0)
#     t.act(Action.CHECK, 'a', 0.0)
#     street = t.state().round.street
#     assert street == 'flop', street
#     # flop
#     t.act(Action.CHECK, 'a', 0.0)
#     t.act(Action.CHECK, 'b', 0.0)
#     street = t.state().round.street
#     assert street == 'turn', street
#     # turn
#     t.act(Action.CHECK, 'a', 0.0)
#     t.act(Action.CHECK, 'b', 0.0)
#     street = t.state().round.street
#     assert street == 'river', street
#     # river
#     t.act(Action.CHECK, 'a', 0.0)
#     t.act(Action.CHECK, 'b', 0.0)
#     street = t.state().round.street
#     assert street == 'showdown', street
#     # Hand 2
#     t.new_round()
#     # preflop
#     t.act(Action.CALL, 'a', 1.0)
#     t.act(Action.CHECK, 'b', 0.0)
#     # flop
#     t.act(Action.CHECK, 'b', 0.0)
#     t.act(Action.CHECK, 'a', 0.0)
#     # turn
#     t.act(Action.CHECK, 'b', 0.0)
#     t.act(Action.CHECK, 'a', 0.0)
#     # river
#     t.act(Action.CHECK, 'b', 0.0)
#     t.act(Action.CHECK, 'a', 0.0)
# 
# 
