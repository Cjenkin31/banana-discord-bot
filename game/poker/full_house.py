from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class FullHouse(PokerHand):
    def __init__(self, value):
        super().__init__(value)
        self.triplet_rank = None
        self.pair_rank = None

    def makes_hand(self, hand):
        super().makes_hand(hand)

        best_triplet_rank = None
        best_pair_rank = None

        for rank in self.unique_ranks:
            count = 0
            for card in self.cards:
                if card.rank == rank:
                    count += 1

            if count >= 2:
                if count > 2:
                    if best_triplet_rank is None:
                        best_triplet_rank = rank
                    elif best_pair_rank is None:
                        best_pair_rank = rank
                elif best_pair_rank is None:
                    best_pair_rank = rank

            if best_triplet_rank is not None and best_pair_rank is not None:
                self.triplet_rank = best_triplet_rank
                self.pair_rank = best_pair_rank
                return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for card in self.cards:
            if card.rank == self.triplet_rank:
                hand_cards.append(card)
        for card in self.cards:
            if card.rank == self.pair_rank:
                hand_cards.append(card)
        return hand_cards[0:5]

    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.triplet_rank] > card_rank_values[hand.triplet_rank]:
            return 1
        if card_rank_values[self.triplet_rank] < card_rank_values[hand.triplet_rank]:
            return -1

        if card_rank_values[self.pair_rank] > card_rank_values[hand.pair_rank]:
            return 1
        if card_rank_values[self.pair_rank] < card_rank_values[hand.pair_rank]:
            return -1
        return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Full House"

    def get_detailed_name(self):
        return "Full House (" + self.triplet_rank + ", " + self.pair_rank + ")"