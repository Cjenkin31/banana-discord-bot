from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class TwoPair(PokerHand):
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
                    self.best_pair = best_pair_rank
                    self.second_pair = rank
                    return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for card in self.cards:
            if card.rank == self.best_pair or card.rank == self.second_pair:
                hand_cards.append(card)
        return hand_cards
    
    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.best_pair] > card_rank_values[hand.best_pair]:
            return 1
        elif card_rank_values[self.best_pair] < card_rank_values[hand.best_pair]:
            return -1

        if card_rank_values[self.second_pair] > card_rank_values[hand.second_pair]:
            return 1
        elif card_rank_values[self.second_pair] < card_rank_values[hand.second_pair]:
            return -1
        else:
            return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Two Pair"

    def get_detailed_name(self):
        return "Two Pair (" + self.best_pair + ", " + self.second_pair + ")"