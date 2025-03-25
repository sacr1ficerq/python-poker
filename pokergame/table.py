from .deck import Deck
from itertools import combinations


def evaluate(cards):
    rank_order = '23456789TJQKA'
    suits = 'cdhs'
    ranks = sorted([rank_order.index(c[0]) for c in cards], reverse=True)
    suits_count = [c[1] for c in cards]

    is_flush = any(suits_count.count(s) >= 5 for s in suits)
    is_straight = False
    unique_ranks = list(sorted(set(ranks), reverse=True))

    # Check for straight
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i+4] == 4:
            is_straight = True
            break

    # Special case for wheel (A-2-3-4-5)
    if set([12, 0, 1, 2, 3]).issubset(ranks):
        is_straight = True

    rank_counts = [ranks.count(r) for r in set(ranks)]
    rank_counts.sort(reverse=True)

    # Determine hand strength
    if is_straight and is_flush and 12 in ranks and 11 in ranks and 10 in ranks:
        return ("Royal Flush", [])
    elif is_straight and is_flush:
        return ("Straight Flush", unique_ranks[:5])
    elif rank_counts[0] == 4:
        return ("Four of a Kind", [r for r in ranks if ranks.count(r) == 4] + 
                                 [r for r in ranks if ranks.count(r) != 4][:1])
    elif rank_counts[0] == 3 and rank_counts[1] >= 2:
        return ("Full House", [r for r in ranks if ranks.count(r) == 3][:3]
                             + [r for r in ranks if ranks.count(r) >= 2 and ranks.count(r) != 3][:2])
    elif is_flush:
        flush_ranks = [r for r, s in zip(ranks, suits_count) if suits_count.count(s) >= 5]
        return ("Flush", sorted(flush_ranks, reverse=True)[:5])
    elif is_straight:
        return ("Straight", unique_ranks[:5])
    elif rank_counts[0] == 3:
        return ("Three of a Kind", [r for r in ranks if ranks.count(r) == 3] + 
                                  [r for r in ranks if ranks.count(r) != 3][:2])
    elif rank_counts[0] == 2 and rank_counts[1] == 2:
        pairs = sorted([r for r in set(ranks) if ranks.count(r) == 2], reverse=True)
        kicker = [r for r in ranks if r not in pairs][0]
        return ("Two Pair", pairs[:2] + [kicker])
    elif rank_counts[0] == 2:
        pair = [r for r in ranks if ranks.count(r) == 2][0]
        kickers = sorted([r for r in ranks if r != pair], reverse=True)[:3]
        return ("Pair", [pair] + kickers)
    else:
        return ("High Card", sorted(ranks, reverse=True)[:5])


def evaluate_hand(board, players_cards):
    """players_cards
    Args:
        board: List of community cards
        *players_cards: Variable number of player card lists
    Returns:
        Dictionary with each player's best hand combination
    """

    hand_rankings = [
        "High Card",
        "Pair",
        "Two Pair",
        "Three of a Kind",
        "Straight",
        "Flush",
        "Full House",
        "Four of a Kind",
        "Straight Flush",
        "Royal Flush"
    ]

    results = []
    for i, player in enumerate(players_cards):
        # Generate all possible 5-card combinations from board + player cards
        possible_hands = list(combinations(board + list(player), 5))
        best_hand = None
        rank = None

        for hand in possible_hands:
            current_hand = evaluate(list(hand))
            current_rank = hand_rankings.index(current_hand[0])
            if best_hand is None:
                best_hand = current_hand
                rank = current_rank
                continue
            best_rank = hand_rankings.index(best_hand[0])
            if current_rank > best_rank:
                best_hand = current_hand
                rank = current_rank
                continue
            current_kicker = current_hand[1]
            best_kicker = best_hand[1]
            if current_rank == best_rank and current_kicker > best_kicker:
                best_hand = current_hand
                rank = current_rank

        results.append({
            "cards": player,
            "rank": rank,
            "best_hand": best_hand[0],
            "combination": best_hand[1]
        })

    return results


class Round:
    def __init__(self, players, table):
        # players in game (including all_in) sorted by left to act
        first = table.button + 1

        self.players = players[first:] + players[:first]
        assert len(players) >= 2, 'not enough players'

        print('new round')
        print('players:')
        print(*map(lambda p: p.name, self.players), sep='\n')

        self.table = table

        self.sb = table.sb
        self.bb = table.bb

        self.street = 'preflop'
        self.deck = Deck()
        self.pot = 0
        self.max_bet = 0
        self.board = []

    # streets
    def preflop(self):
        self.street = 'preflop'
        # deal cards
        for p in self.players:
            cards = [self.deck.pop(), self.deck.pop()]
            p.deal(cards)
        n = len(self.players)

        # blinds
        if n == 2:
            sb = 1
            bb = 0
        else:
            sb = 0
            bb = 1

        for p in self.players:
            p.is_acting = False
            p.chips_bet = 0

        self.players[sb].is_acting = True
        self.players[sb].blind(self.sb)
        self.players[bb].blind(self.bb)

    def flop(self):
        self.street = 'flop'
        # deal flop
        flop_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        print(f'flop: {flop_cards}')
        self.board = flop_cards

    def turn(self):
        self.street = 'turn'
        # deal turn
        turn_cards = [self.deck.pop()]
        print(f'turn: {turn_cards}')
        self.board += turn_cards

    def river(self):
        self.street = 'river'
        # deal river
        river_cards = [self.deck.pop()]
        print(f'river: {river_cards}')
        self.board += river_cards

    def showdown(self):
        print('showdown:')
        print('board:', self.board)

        nom = list(map(str, range(2, 9+1))) + list('TJQKA')

        def high_card(cards):
            return max(cards, key=lambda c: nom.index(c[:-1]))[:-1]

        players_cards = [p.cards for p in self.players]
        evals = evaluate_hand(self.board, players_cards)

        def rank(pair):
            return (pair[0]['rank'], pair[0]['combination'])

        pairs = sorted(zip(evals, range(len(self.players))), key=rank, reverse=True)
        winners = []
        for p in pairs:
            if p[0]['combination'] != pairs[0][0]['combination']:
                break
            winners.append(self.players[p[1]].name)

        print(*evals, sep='\n')
        print('winners:', winners)

        self.win(winners)

    def action(self, delta):
        self.pot += delta
        """
        Called after player acted
        delta: pot-after-action - pot-before-action
        """

        def in_game_f(p):
            return not p.folded

        self.players = list(filter(in_game_f, self.players))
        assert len(self.players) != 0, 'no one playing'

        if len(self.players) == 1:
            self.win([self.players[0].name])
            return

        self.max_bet = max(self.players, key=lambda p: p.chips_bet).chips_bet

        def to_act_f(p):
            return not p.all_in and p.chips_bet != self.max_bet or not p.acted

        # check how many left to act
        to_act = list(filter(to_act_f, self.players))
        if len(to_act) == 0:
            self.next_street()
            return

        # next to act
        for i, p in enumerate(self.players):
            if p.is_acting:
                p.is_acting = False
                next_p = to_act[(i + 1) % len(to_act)]
                next_p.is_acting = True

                # print(f'now action on player {next_p.name}')
                break

    def next_street(self):
        for p in self.players:
            p.is_acting = False
            p.chips_bet = 0
            p.acted = False
        self.players[0].is_acting = True
        self.max_bet = 0

        if self.street == 'preflop':
            self.flop()
        elif self.street == 'flop':
            self.turn()
        elif self.street == 'turn':
            self.river()
        elif self.street == 'river':
            self.showdown()

    def win(self, player_names):
        winners = []  # TODO: manage situations with all_ins
        for p in self.players:
            if p.name in player_names:
                winners.append(p)
        assert len(winners) != 0, 'no winners'
        for w in winners:
            w.stack += self.pot / len(winners)

        print('winners:', winners)
        self.table.new_round()

    def state(self):
        in_game = [p.name for p in self.players]
        res = {'players': in_game,
               'street': self.street,
               'pot': self.pot}
        return res


class Table:
    def __init__(self, sb, bb):
        self.bb = bb
        self.sb = sb
        self.players = []
        self.button = 0  # button index

        self.current_round = None

    def add_player(self, player):
        self.players.append(player)

    def state(self, player_name):
        players = [p.state(show_cards=(player_name == p.name)) for p in self.players]
        res = {'players': players, 'button': self.button}
        if self.current_round:
            res['round'] = self.current_round.state()
        return res

    def new_round(self):
        self.button = (self.button + 1) % len(self.players)
        self.current_round = Round(self.players, self)
        self.current_round.preflop()

    def __repr__(self):
        return f'sb: {self.sb}\t bb: {self.bb}\nplayers: {self.players}'
