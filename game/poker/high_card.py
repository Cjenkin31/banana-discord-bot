from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class HighCard(PokerHand):
    def makes_hand(self, hand):
        super().makes_hand(hand)

        if len(self.cards):
            self.rank = self.cards[0].rank
            return True
        else:
            return False

    def get_hand_cards(self):
        for card in self.cards:
            if card.rank == self.rank:
                return [card]
        return []
    
    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.rank] > card_rank_values[hand.rank]:
            return 1
        elif card_rank_values[self.rank] < card_rank_values[hand.rank]:
            return -1
        else:
            return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "High Card"

    def get_detailed_name(self):
        return "High Card (" + self.rank + ")"