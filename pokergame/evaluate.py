from itertools import combinations
from typing import Tuple, List, Dict

def evaluate(cards: List[str]) -> Tuple[str, List]:
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


def evaluate_hand(board: List[str], players_cards: List[Tuple[str, str]]) -> List[Dict]:
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
    for cards in players_cards:
        # Generate all possible 5-card combinations from board + cards cards
        assert len(board) == 5, 'Wrong board: ' + ','.join(board)
        assert len(cards) == 2, 'Wrong player card: ' + ','.join(cards)
        possible_hands: List[Tuple[str, str, str, str, str]] = list(combinations(board + list(cards), 5))
        assert len(possible_hands) != 0, 'Wrong board or players cards:' + ','.join(board) +'; '+','.join(cards)

        best_hand: Tuple[str, list] = evaluate(list(possible_hands[0]))
        rank: int = hand_rankings.index(best_hand[0])

        for hand in possible_hands:
            current_hand = evaluate(list(hand))
            current_rank = hand_rankings.index(current_hand[0])
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
            "cards": cards,
            "rank": rank,
            "best_hand": best_hand[0],
            "combination": best_hand[1]
        })

    return results

