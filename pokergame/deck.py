import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from typing import Dict, List

suits = list('shdc')
ranks = list('AKQJT98765432')

class Card:
    def __init__(self, idx:int|None=None, s:str|None=None):
        assert idx is not None or s is not None
        assert idx is None or s is None
        if idx is not None:
            assert idx >= 0 and idx < 52
            # 2s3s4s..As2h3h...Ac
            self.suit = idx // 13
            self.rank = idx % 13
            self.idx = idx
            return
        if s is not None:
            assert len(s) == 2
            self.rank = ranks.index(s[0])
            self.suit = suits.index(s[1])
            self.idx = self.suit * 13 + self.rank
            return
        assert False
            
    def __repr__(self):
        return f'{ranks[self.rank]}{suits[self.suit]}'


class Holding:
    def __init__(self, c1: Card|None=None, c2: Card|None=None, s:str|None=None):
        if s is not None:
            assert c1 is None and c2 is None 
            assert len(s) == 4
            c1 = Card(s=s[:2])
            c2 = Card(s=s[2:])

        assert c1 is not None and c2 is not None
        assert c1.idx != c2.idx
        # sort by rank
        # c1 <= c2
        c1, c2 = sorted([c1, c2], key=lambda x: x.rank)
        self.c1 = c1
        self.c2 = c2

        # poket pair
        if c1.rank == c2.rank:
            self.idx = (c1.rank, c1.rank)
        # suited
        elif c1.suit == c2.suit:
            # y < x
            self.idx = (c1.rank, c2.rank)
        # offsuit
        else:
            self.idx = (c2.rank, c1.rank)

    def __repr__(self):
        return f'{self.c1} {self.c2}'

# Custom color gradient (white to dark green)
colors = ["#ffffff", "#e5f5e0", "#a1d99b", "#31a354"]
cmap = LinearSegmentedColormap.from_list("poker", colors)

class Range:
    def __init__(self, matrix=None):
        if matrix is None:
            matrix = np.zeros((13, 13))
        assert matrix.shape==(13, 13)
        # Initialize 13x13 matrix (AA at [0,0], 22 at [12,12])
        self._range = matrix
    
    def set_holding(self, h: Holding, p: float) -> None:
        assert p >= 0 and p <= 1
        i, j = h.idx
        self._range[i, j] = p
    
    def get_holding(self, h: Holding) -> float:
        i, j = h.idx
        return self._range[i, j]

    def display(self) -> None:
        _, ax = plt.subplots(figsize=(5, 5))
        
        # Remove all ticks and borders
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.imshow(self._range, cmap=cmap, vmin=0, vmax=1)
        
        for i in range(14):
            ax.axhline(i-0.5, color='black', linewidth=0.5, alpha=0.5)
            ax.axvline(i-0.5, color='black', linewidth=0.5, alpha=0.5)
        
        # Add hand labels inside each cell
        for i in range(13):
            for j in range(13):
                # Pocket pairs (AA, KK, ..., 22)
                label = ''
                if i == j:
                    label = f"{ranks[i]}{ranks[j]}"
                elif i < j:
                    label = f"{ranks[i]}{ranks[j]}s"
                else:
                    label = f"{ranks[j]}{ranks[i]}o"
                
                ax.text(j, i, label, ha='center', va='center', fontsize=10)

        ax.set_aspect('equal') # Make cells square
        plt.tight_layout()
        plt.show()

    def todict(self) -> Dict[str, float]:
        d = {}
        for i in range(13):
            for j in range(13):
                p = self._range[i, j] 
                if p != 0:
                    c1, c2 = ranks[i], ranks[j]
                    h = ''
                    if i > j:
                        h = f'{c1}{c2}o'
                    elif i == j:
                        h = f'{c1}{c2}'
                    else:
                        h = f'{c1}{c2}s'
                    d[h] = p
        return d

    def __repr__(self) -> str:
        return self.todict().__str__()
                    

class Deck:
    def __init__(self):
        # Initialize card availability (1 = available, 0 = blocked)
        self.card_live = np.ones(52, dtype=bool)  

    def sample_hand(self, r: Range) -> Holding: # As, Ah
        # sample combination
        # assign suit
        p = np.zeros([52, 52])
        for i in range(52):
            if not self.card_live[i]:
                continue
            for j in range(52):
                if not self.card_live[j] or i == j:
                    continue
                # both cards live
                c1, c2 = Card(idx=i), Card(idx=j)
                h = Holding(c1, c2)
                p[j, i] = r.get_holding(h)
        res = np.random.choice(52*52, p = p.flatten() / p.flatten().sum())
        idx1, idx2 = res // 52, res % 52
        self.card_live[idx1] = False
        self.card_live[idx2] = False
        return Holding(Card(idx1), Card(idx2))

    def sample_runout(self, n: int) -> List[Card]:
        live = self.card_live.copy()
        res = []
        for i in range(n):
            idx = np.random.choice(52, p=live / live.sum())
            live[idx] = 0
            res.append(Card(idx=idx))
        return res

    def pop(self) -> Card:
        d = self.card_live.sum()
        assert d > 0
        p = self.card_live / d
        res = np.random.choice(52, p=p)
        self.card_live[res] = False
        return Card(res)

