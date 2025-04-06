from pokergame.table import Table
from pokergame.player import Action

import pytest


def test_checkdown_1():
    # create table
    t = Table('', sb=1, bb=2)

    # add/remove players
    t.add_player(1, 'zamazer', 100)
    t.add_player(2, 'mamaz', 200)
    # pretty_print(t.state())

    # start game
    t.start_game()

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


def test_checkdown_2():
    t = Table('', sb=1, bb=2)
    t.add_player(1, 'a', 100)
    t.add_player(2, 'b', 100)
    # start game
    t.start_game()
    print(t.current_round.players)  # a, b

    # b is dealer
    # Hand 1
    # preflop
    t.act(Action.CALL, 'b', 1.0)
    t.act(Action.CHECK, 'a', 0.0)
    street = t.state().round.street
    assert street == 'flop', street
    # flop
    t.act(Action.CHECK, 'a', 0.0)
    t.act(Action.CHECK, 'b', 0.0)
    street = t.state().round.street
    assert street == 'turn', street
    # turn
    t.act(Action.CHECK, 'a', 0.0)
    t.act(Action.CHECK, 'b', 0.0)
    street = t.state().round.street
    assert street == 'river', street
    # river
    t.act(Action.CHECK, 'a', 0.0)
    t.act(Action.CHECK, 'b', 0.0)
    street = t.state().round.street
    assert street == 'showdown', street
    # Hand 2
    t.new_round()
    # preflop
    t.act(Action.CALL, 'a', 1.0)
    t.act(Action.CHECK, 'b', 0.0)
    # flop
    t.act(Action.CHECK, 'b', 0.0)
    t.act(Action.CHECK, 'a', 0.0)
    # turn
    t.act(Action.CHECK, 'b', 0.0)
    t.act(Action.CHECK, 'a', 0.0)
    # river
    t.act(Action.CHECK, 'b', 0.0)
    t.act(Action.CHECK, 'a', 0.0)


