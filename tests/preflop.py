from pokergame.table import Table
from pokergame.player import Action

import pytest


@pytest.fixture
def t():
    table = Table('test_table', sb=0.5, bb=1)
    table.add_player(1, 'BB', 100)
    table.add_player(2, 'BUT', 100)
    table.start_game()
    return table


@pytest.fixture
def players(t):
    return {p.name: p for p in t.players}


def test_small_blind_call(t, players):
    t.act(Action.CALL, 'BUT', 0.5)

    assert players['BB'].stack == 99
    assert players['BUT'].stack == 99


def test_fold(t, players):
    t.act(Action.FOLD, 'BUT', 0.0)

    assert players['BB'].stack == 100.5
    assert players['BUT'].stack == 99.5


def test_raise(t, players):
    t.act(Action.RAISE, 'BUT', 7.0)
    t.act(Action.FOLD, 'BB', 0.0)

    assert players['BUT'].stack == 101
    assert players['BB'].stack == 99


def test_wrong_amount_call(t):
    t.act(Action.RAISE, 'BUT', 10.0)  # total bet is 12

    with pytest.raises(AssertionError):
        t.act(Action.CALL, 'BB', 0.0)


def test_wrong_amount_raise_1(t):
    assert t.state()['round']['minBetAmount'] == 1.5
    with pytest.raises(AssertionError):
        t.act(Action.RAISE, 'BUT', 1.49)


def test_wrong_amount_raise_2(t):
    t.act(Action.RAISE, 'BUT', 1.5)  # 0.5 + 1.5 = 2bb
    min_bet = t.state()['round']['minBetAmount']
    assert min_bet == 2.0, f'{min_bet}' # 3bb min bet
