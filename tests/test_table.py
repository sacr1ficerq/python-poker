from pokergame.table import Table
from pokergame.player import Action, Player
from pokergame.deck import Range, Holding

from json import dumps
import pytest
from typing import List, Dict

from fixtures import *

class TestBasic:
    def test_create(self, range_sb: Range, range_bb: Range):
        # add/remove players
        table = Table('test_table', SB, BB)
        table.add_player(0, 'BB', DEPTH, range_bb)
        table.add_player(1, 'BUT', DEPTH, range_sb)

    def test_start(self, table: Table):
        # add/remove players
        table.start_game(STARTING_POT)

    def test_deal(self, table: Table, players: Dict[str, Player]):
        table.start_game(STARTING_POT)
        assert players['BB'].holding is not None
        assert players['BUT'].holding is not None


class TestState:
    def test_create(self, table: Table):
        table.state()
        dumps(table.data())

    def test_start(self, table: Table, players: List[Player]):
        table.start_game(STARTING_POT)
        table.state()
        dumps(table.data())
        dumps(table.private_data('BB'))
        dumps(table.private_data('BUT'))
