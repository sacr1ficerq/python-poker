from pokergame import Deck, Range, Card, Holding, Round, Street, Action
import pytest
from typing import List, Dict

from fixtures import *
from pokergame.states import PlayerState

from json import dumps

class TestBasic:
    def test_start(self, round: Round, players: Dict[str, Player]):
        # Game started
        assert players['BB'].profit + players['BUT'].profit == 0
        assert round.street == Street.FLOP
        assert players['BB'].holding != None

        assert round.min_bet_amount == BB
        print('BB range: ', players['BB'].preflop_range)
        print('BB has: ', players['BB'].holding)

        assert players['BUT'].holding != None
        print('BUT range: ', players['BUT'].preflop_range)
        print('BUT has: ', players['BUT'].holding)

        assert round.pot == STARTING_POT

    def test_checkdown(self, play: Callable, players: Dict[str, Player]):
        assert players['BB'].profit + players['BUT'].profit == 0
        line = ('x x').split() + ('x x').split() + ('x x').split()
        play(line)
        assert players['BB'].profit + players['BUT'].profit == 0

class TestBasicLines:
    def test_cbet(self, play: Callable):
        line = ('x b3.0 c3.0').split() + ('x x').split() + ('x x').split()
        play(line)

    def test_xr(self, play: Callable):
        line = ('x b3.0 r9.0 f').split()
        play(line)

    def test_bxb(self, play: Callable):
        line = ('x b3.0 c3.0').split() + ('x x').split() + ('x b12.0 c12.0').split()
        play(line)


class TestLines:
    def test_lines(self, play: Callable, range_sb, range_bb):
        lines: List[List[str]] = [
            ['f'],
            ['b3.0 f'],
            ['x x', 'b3.0 f'],
            ['x b3.0 c3.0', 'x x', 'x x'],
            ['x b3.0 c3.0', 'x x', 'x b3.0 c3.0'],
        ]
        for i, e in enumerate(lines):
            print(f"line: {' - '.join(e)}")
            line = []
            for street in e:
                line += street.split()
            t = Table(str(i), starting_pot=STARTING_POT, depth=DEPTH, sb=SB, bb=BB)
            t.add_player(0, 'BB', DEPTH, range_bb)
            t.add_player(1, 'BUT', DEPTH, range_sb)
            play(line, t)
            dumps(t.data())


class TestAllIn:
    pass

class TestShowdown:
    pass
