from collections import Counter

class HandEvaluator:
    @staticmethod
    def evaluate_hand(hand):
        values = sorted([HandEvaluator.rank_to_value(card[0]) for card in hand], reverse=True)
        is_flush = len(set(suit for _, suit in hand)) == 1
        is_straight = HandEvaluator.is_straight(values)

        if is_flush and is_straight:
            return "Straight Flush", values
        elif HandEvaluator.is_four_of_a_kind(values):
            return "Four of a Kind", values
        elif HandEvaluator.is_full_house(values):
            return "Full House", values
        elif is_flush:
            return "Flush", values
        elif is_straight:
            return "Straight", values
        elif HandEvaluator.is_three_of_a_kind(values):
            return "Three of a Kind", values
        elif HandEvaluator.is_two_pair(values):
            return "Two Pair", values
        elif HandEvaluator.is_one_pair(values):
            return "One Pair", values
        else:
            return "High Card", values

    @staticmethod
    def compare_hands(hand1, hand2):
        score1, high_card1 = HandEvaluator.evaluate_hand(hand1)
        score2, high_card2 = HandEvaluator.evaluate_hand(hand2)

        hand_rankings = [
            'High Card', 'One Pair', 'Two Pair', 'Three of a Kind', 'Straight',
            'Flush', 'Full House', 'Four of a Kind', 'Straight Flush'
        ]

        if hand_rankings.index(score1) > hand_rankings.index(score2):
            return 1
        elif hand_rankings.index(score1) < hand_rankings.index(score2):
            return -1
        else:
            for hc1, hc2 in zip(high_card1, high_card2):
                if hc1 > hc2:
                    return 1
                elif hc1 < hc2:
                    return -1
            return 0

    @staticmethod
    def rank_to_value(rank):
        rank_values = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return int(rank) if rank.isdigit() else rank_values.get(rank, rank)

    @staticmethod
    def is_straight(values):
        return all(values[i] - 1 == values[i + 1] for i in range(len(values) - 1))

    @staticmethod
    def is_four_of_a_kind(values):
        return 4 in Counter(values).values()

    @staticmethod
    def is_full_house(values):
        value_counts = Counter(values).values()
        return 3 in value_counts and 2 in value_counts

    @staticmethod
    def is_three_of_a_kind(values):
        return 3 in Counter(values).values()

    @staticmethod
    def is_two_pair(values):
        return list(Counter(values).values()).count(2) == 2

    @staticmethod
    def is_one_pair(values):
        return 2 in Counter(values).values()
