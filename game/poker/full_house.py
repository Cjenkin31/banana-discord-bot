from game.poker.poker_hand import PokerHand;
from game.poker.poker_hand import card_rank_values

class FullHouse(PokerHand):
    def makes_hand(self, hand):
        super().makes_hand(hand)

        best_triple_rank = None
        best_pair_rank = None

        for rank in self.unique_ranks:
            count = 0
            for card in self.cards:
                if card.rank == rank:
                    count += 1

            if (count > 2):
                if (best_triple_rank is None):
                    best_triple_rank = rank
                else:
                    best_pair_rank = rank
            elif count == 2:
                best_pair_rank = rank

            if best_triple_rank is not None and best_pair_rank is not None:
                self.triple_rank = best_triple_rank
                self.pair_rank = best_pair_rank
                return True

        return False

    def get_hand_cards(self):      
        hand_cards = []
        for card in self.cards:
            if card.rank == self.triple_rank:
                hand_cards.append(card)     
        for card in self.cards:
            if card.rank == self.pair_rank:
                hand_cards.append(card)
        return hand_cards[0:5]
    
    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.triple_rank] > card_rank_values[hand.triple_rank]:
            return 1
        elif card_rank_values[self.triple_rank] < card_rank_values[hand.triple_rank]:
            return -1

        if card_rank_values[self.pair_rank] > card_rank_values[hand.pair_rank]:
            return 1
        elif card_rank_values[self.pair_rank] < card_rank_values[hand.pair_rank]:
            return -1
        else:
            return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Full House"

    def get_detailed_name(self):
        return "Full House (" + self.triple_rank + ", " + self.pair_rank + ")"