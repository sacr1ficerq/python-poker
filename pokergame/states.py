from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum


class Street(Enum):
    PREFLOP = 'preflop'
    FLOP = 'flop'
    TURN = 'turn'
    RIVER = 'river'
    SHOWDOWN = 'showdown'


class Action(Enum):
    FOLD = 'fold'
    CHECK = 'check'
    CALL = 'call'
    BET = 'bet'
    RAISE = 'raise'


class PlayerState(Enum):
    BASE = ''
    FOLDED = 'folded'
    ALLIN = 'all-in'
    ACTING = 'acting'
    WINNING = 'winning'
    LOOSING = 'loosing'
    SITOUT = 'sit-out'


@dataclass
class PlayerData:
    # id: str
    name: str
    stack: float
    profit: float
    state: str
    bet: float
    lastAction: Optional[str]
    cards: Optional[Tuple[str, str]] = None


@dataclass
class RoundData:
    street: str
    maxBet: float
    board: List[str]
    pot: float
    maxBetAmount: float
    minBetAmount: float
    roundEnded: bool
    button: str


@dataclass
class TableData:
    players: List[dict]
    round: Optional[dict]
    depth: float
    startingPot: float
    handsPlayed: int
