from pokergame.table import Table
from pokergame.player import Action

from json import dumps


import pytest

@pytest.fixture
def t():
    table = Table('test_table', sb=0.5, bb=1)
    table.add_player(0, 'BB', 100)
    table.add_player(1, 'BUT', 100)
    return table


@pytest.fixture
def players(t):
    return {p.name: p for p in t.players}


def test_state(t: Table, players):
    t.state()
    dumps(t.data())
    dumps(t.private_data('BB'))

    t.start_game()
    dumps(t.data())
    t.act(Action.FOLD, 'BUT', 0)
    dumps(t.data())
