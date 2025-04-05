from pokergame.table import Table
from pokergame.player import Action

import pytest


@pytest.fixture
def t():
    table = Table('test_table', sb=1, bb=2)
    table.add_player(1, 'BB', 100)
    table.add_player(2, 'BUT', 100)
    table.start_game()
    return table


@pytest.fixture
def players(t):
    return {p.name: p for p in t.players}


def test_small_blind_call(t, players):
    t.act(action=Action.CALL, player_name='BUT', amount=1.0)

    assert players['BB'].stack == 98
    assert players['BUT'].stack == 98


def test_fold(t, players):
    t.act(Action.FOLD, 'BUT', 0.0)

    assert players['BB'].stack == 101
    assert players['BUT'].stack == 99


def test_raise(t, players):
    t.act(Action.RAISE, 'BUT', 7.0)
    t.act(Action.FOLD, 'BB', 0.0)

    assert players['BUT'].stack == 102
    assert players['BB'].stack == 98


def test_wrong_amount_call(t):
    t.act(Action.RAISE, 'BUT', 10.0)  # total bet is 12

    with pytest.raises(AssertionError):
        t.act(Action.CALL, 'BB', 0.0)
