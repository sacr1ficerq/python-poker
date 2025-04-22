from pokergame import Deck, Range, Card, Holding, Table, Player, Round

from typing import Dict
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
    rng.set_holding(Holding(s='QcQh'), 0.2)     
    rng.set_holding(Holding(s='JcJh'), 0.2)     
    return rng

@pytest.fixture
def table(range_sb, range_bb) -> Table:
    table = Table('test_table', SB, BB)
    table.add_player(0, 'BB', DEPTH, range_bb)
    table.add_player(1, 'BUT', DEPTH, range_sb)
    return table

@pytest.fixture
def players(table) -> Dict[str, Player]:
    return {p.name: p for p in table.players}

@pytest.fixture
def round(table: Table) -> Round:
    table.start_game(STARTING_POT)
    assert table.current_round is not None
    return table.current_round

