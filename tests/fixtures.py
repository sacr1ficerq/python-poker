from pokergame import Deck, Range, Card, Holding, Table, Player, Round, Action

from typing import Dict, List, Callable
import pytest

SB = 0.5
BB = 1
DEPTH = 120
STARTING_POT = BB * 12

@pytest.fixture(autouse=True)
def setup_logging():
    import logging
    logging.basicConfig(level=logging.INFO)

@pytest.fixture
def range_sb() -> Range:
    rng = Range()
    rng.set_holding(Holding(s='AcAh'), 0.8)     
    rng.set_holding(Holding(s='JsAc'), 0.2)     
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
    table = Table('test_table', starting_pot=STARTING_POT, depth=DEPTH, move_button=True, sb=SB, bb=BB)
    but = Player('0', 'BUT', DEPTH, range_sb, table)
    bb = Player('1', 'BB', DEPTH, range_bb, table)
    table.add_player(but)
    table.add_player(bb)
    return table

@pytest.fixture
def players(table) -> Dict[str, Player]:
    return {p.name: p for p in table.players}

@pytest.fixture
def round(table: Table) -> Round:
    table.start_game()
    assert table.current_round is not None
    return table.current_round


@pytest.fixture
def play(table: Table) -> Callable:
    def res(line: List[str], table=table):
        table.start_game()
        # Example: ['b3.0', 'c', 'x', 'x', 'x', 'x']
        players = ['BB', 'BUT']
        round = table.current_round
        assert round is not None
        acting = players[round.acting]
        print('acting:', acting)

        for a in line:
            match a[0]:
                case 'f':
                    table.act(Action.FOLD, acting, 0)
                case 'x':
                    table.act(Action.CHECK, acting, 0)
                case 'c':
                    amount = float(a[1:])
                    table.act(Action.CALL, acting, amount)
                case 'b':
                    amount = float(a[1:])
                    table.act(Action.BET, acting, amount)
                case 'r':
                    amount = float(a[1:])
                    table.act(Action.RAISE, acting, amount)
                case default:
                    assert False, f"wrong action: '{a}'"
            acting = players[round.acting]
    return res

