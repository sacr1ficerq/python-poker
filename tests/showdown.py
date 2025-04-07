from pokergame.table import Table
from pokergame.player import Action

import pytest

SB = 0.5
BB = 1


@pytest.fixture
def t():
    table = Table('test_table', SB, BB)
    table.add_player(0, 'BB', 100)
    table.add_player(1, 'BUT', 100)
    table.start_game()
    return table


@pytest.fixture
def players(t):
    return {p.name: p for p in t.players}


def test_showdown_1(t, players):
    # preflop
    t.act(Action.CALL, 'BUT', SB)
    t.act(Action.CHECK, 'BB', 0.0)
    # flop
    t.act(Action.CHECK, 'BB', 0.0)
    t.act(Action.CHECK, 'BUT', 0.0)
    # turn
    t.act(Action.CHECK, 'BB', 0.0)
    t.act(Action.CHECK, 'BUT', 0.0)
    # river
    t.act(Action.CHECK, 'BB', 0.0)
    t.act(Action.CHECK, 'BUT', 0.0)

    state = t.state()
    street = state.round.street
    assert street == 'showdown', street
    for p in state.players:
        assert p.state == 'winning' or p.state == 'loosing'
