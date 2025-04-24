from dataclasses import dataclass
from .deck import Card, Holding
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
    state: str
    bet: float
    cards: Optional[Tuple[str, str]] = None


@dataclass
class RoundData:
    street: str
    maxBet: float
    board: List[Card]
    pot: float
    maxBetAmount: float
    minBetAmount: float
    roundEnded: bool
    button: str


@dataclass
class TableData:
    players: List[PlayerData]
    round: Optional[RoundData]
