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


def test_all_in_0(t, players):
    # preflop
    t.act(Action.RAISE, 'BUT', players['BUT'].stack)
    hero = players['BUT'].state()
    assert hero.state == 'all-in'


def test_all_in_1(t, players):
    # preflop

    with pytest.raises(AssertionError):
        t.act(Action.RAISE, 'BUT', players['BUT'].stack + 0.001)


def test_all_in_2(t, players):
    # preflop
    assert players['BUT'].stack == DEPTH - SB, players['BUT'].stack
    t.act(Action.RAISE, 'BUT', players['BUT'].stack)
    t.act(Action.CALL, 'BB', DEPTH - BB)

    # flop
    # turn
    # river
    # showdown

    state = t.state()
    street = state.round.street
    board = state.round.board
    assert street == 'showdown', street
    assert len(board) == 3 + 1 + 1, board
    print(state)
    for p in state.players:
        assert p.state == 'winning' or p.state == 'loosing', 'state: ' + p.state


def test_all_in_3(t, players):
    # preflop
    table = Table('test_table', 5, 10)
    table.add_player(0, 'BB', 100)
    table.add_player(1, 'BUT', 200)
    table.start_game()
    table.act(Action.RAISE, 'BUT', 100-5)
    table.act(Action.CALL, 'BB', 100-10)

    for p in table.state().players:
        assert (p.state == 'loosing') \
            or (p.state == 'winning'), \
            table.state().players


def test_all_in_4(t, players):
    # preflop
    table = Table('test_table', 5, 10)
    table.add_player(0, 'BB', 200)
    table.add_player(1, 'BUT', 100)
    table.start_game()
    table.act(Action.RAISE, 'BUT', 100-5)
    table.act(Action.CALL, 'BB', 100-10)

    for p in table.state().players:
        assert (p.state == 'loosing') \
            or (p.state == 'winning'), \
            table.state().players


def test_all_in_blind_1():
    # preflop
    table = Table('test_table', 5, 10)
    table.add_player(0, 'BB', 10)
    table.add_player(1, 'BUT', 10)
    table.start_game()


def test_all_in_blind_2():
    # preflop
    table = Table('test_table', 5, 10)
    table.add_player(0, 'BB', 9)
    table.add_player(1, 'BUT', 9)
    table.start_game()

    player = table.get_player('BUT').state()
    assert player.state == 'acting'
    assert table.state().round.maxBetAmount == 4

    table.act(Action.CALL, 'BUT', 4)
    for p in table.state().players:
        assert (p.stack == 0 and p.state == 'loosing') \
            or (p.stack == 18 and p.state == 'winning'), \
            table.state().players


def test_all_in_blind_3():
    # preflop
    table = Table('test_table', 5, 10)
    table.add_player(0, 'BB', 5)
    table.add_player(1, 'BUT', 5)
    table.start_game()
    for p in table.state().players:
        assert (p.stack == 0 and p.state == 'loosing') \
            or (p.stack == 10 and p.state == 'winning'), \
            table.state().players


def test_all_in_blind_4():
    # preflop
    table = Table('test_table', 5, 10)
    table.add_player(0, 'BB', 4)
    table.add_player(1, 'BUT', 4)
    table.start_game()
    for p in table.state().players:
        assert (p.stack == 0 and p.state == 'loosing') \
            or (p.stack == 8 and p.state == 'winning'), \
            table.state().players
