from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class TwoPair(PokerHand):
    def __init__(self, value):
        super().__init__(value)
        self.high_pair = None
        self.low_pair = None

    def makes_hand(self, hand):
        super().makes_hand(hand)

        best_pair_rank = None

        for rank in self.unique_ranks:
            count = 0
            for card in self.cards:
                if card.rank == rank:
                    count += 1

            if count == 2:
                if best_pair_rank is None:
                    best_pair_rank = rank
                else:
                    self.high_pair = best_pair_rank
                    self.low_pair = rank
                    return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for card in self.cards:
            if card.rank in {self.high_pair, self.low_pair}:
                hand_cards.append(card)
        return hand_cards

    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.high_pair] > card_rank_values[hand.high_pair]:
            return 1
        if card_rank_values[self.high_pair] < card_rank_values[hand.high_pair]:
            return -1

        if card_rank_values[self.low_pair] > card_rank_values[hand.low_pair]:
            return 1
        if card_rank_values[self.low_pair] < card_rank_values[hand.low_pair]:
            return -1
        return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Two Pair"

    def get_detailed_name(self):
        return "Two Pair (" + self.high_pair + ", " + self.low_pair + ")"