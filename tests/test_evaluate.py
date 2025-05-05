from pokergame import Deck, Card, Holding, equity

import time

import pytest
from typing import List

class TestEquity:
    def test_basic(self):
        deck = Deck()
        board: List[Card] = list(map(lambda s: Card(s=s), ['3h', '3c', '3s', '5s']))
        a = Holding(s='KhKc')
        b = Holding(s='AcAh')
        for c in board + [a.c1, a.c2, b.c1, b.c2]:
            deck.card_live[c.idx] = 0
        t = time.time()
        eq: float = equity(deck, a, b, board, 100)
        print(f"time: {(time.time() - t) * 1000: 0.2f} ms")
        print('equity: ', round(eq, 2))
