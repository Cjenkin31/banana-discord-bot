from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class Straight(PokerHand):
    def makes_hand(self, hand):
        super().makes_hand(hand)

        check_ranks = self.unique_ranks.copy()

        if 'A' in check_ranks:
            check_ranks.append('a')

        for r in range(1, len(check_ranks)):
            best_straight = [check_ranks[r - 1]]
            
            count = 0
            for i in range(r, len(check_ranks)):
                if card_rank_values[check_ranks[i - 1]] - card_rank_values[check_ranks[i]] == 1:
                    count += 1
                    if check_ranks[i] == 'a':
                        best_straight.append('A')
                    else:
                        best_straight.append(check_ranks[i])
                else:
                    break

            if count > 3:
                self.ranks = best_straight[0:5]
                return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for rank in self.ranks:
            for card in self.cards:
                if card.rank == rank:
                    hand_cards.append(card)
                    break
        return hand_cards
    
    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.ranks[0]] > card_rank_values[hand.ranks[0]]:
            return 1
        elif card_rank_values[self.ranks[0]] < card_rank_values[hand.ranks[0]]:
            return -1
        else:
            return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Straight"

    def get_detailed_name(self):
        return "Straight (" + self.ranks[0] + ")"