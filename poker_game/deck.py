from random import random


class Deck:
    def __init__(self):
        self.deck = []
        self.fill()
        self.shuffle()

    def fill(self):
        for nom in list(map(str, range(2, 9+1))) + list('TJQKA'):
            for suit in ['s', 'h', 'd', 'c']:
                self.deck.append(nom + suit)

    def shuffle(self):
        # Shuffle the deck array with Fisher-Yates
        for i in range(len(self.deck)):
            j = int(random() * (i + 1))
            tempi = self.deck[i]
            tempj = self.deck[j]
            self.deck[i] = tempj
            self.deck[j] = tempi

    def pop(self):
        assert len(self.deck) != 0
        return self.deck.pop()
