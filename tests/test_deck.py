from pokergame import Deck, Range, Card, Holding
from typing import List, Dict

import pytest

class TestBasic:
    def test_create(self):
        r = Range()
        # Set some sample hands
        r.set_holding(Holding(s='AcAh'), 0.8)     
        r.set_holding(Holding(s='JcAc'), 0.2)     
        # r.display()

    def test_sample(self):
        deck = Deck()
        r1 = Range()
        r1.set_holding(Holding(s='AcAh'), 0.8)     
        r1.set_holding(Holding(s='JcAc'), 0.1)     
        # r1.display()

        r2 = Range()
        r2.set_holding(Holding(s='KcKh'), 0.3)     
        r2.set_holding(Holding(s='JcAc'), 0.3)     
        # r2.display()

        h1 = deck.sample_hand(r1)
        print(f"Player 1: {h1}")

        h2 = deck.sample_hand(r2) 
        print(f"Player 2: {h2}")
