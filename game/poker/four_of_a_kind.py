from game.poker.poker_hand import PokerHand;
from game.poker.poker_hand import card_rank_values

class FourOfAKind(PokerHand):
    def makes_hand(self, hand):
        super().makes_hand(hand)

        for rank in self.unique_ranks:
            count = 0
            for card in self.cards:
                if card.rank == rank:
                    count += 1

            if count == 4:
                self.rank = rank
                return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for card in self.cards:          
            if card.rank == self.rank:
                hand_cards.append(card)
        return hand_cards

    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.rank] > card_rank_values[hand.rank]:
            return 1
        elif card_rank_values[self.rank] < card_rank_values[hand.rank]:
            return -1
        else:
            return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Four Of A Kind"

    def get_detailed_name(self):
        return "Four Of A Kind (" + self.rank + ")"