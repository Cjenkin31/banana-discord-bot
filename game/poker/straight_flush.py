from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class StraightFlush(PokerHand):
    def makes_hand(self, hand):
        super().makes_hand(hand)

        check_ranks = self.unique_ranks.copy()

        if 'A' in check_ranks:
            check_ranks.append('a')

        for r in range(1, len(check_ranks)):
            best_straight_flush = [check_ranks[r - 1]]
            
            count = 0
            for i in range(r, len(check_ranks)):
                if card_rank_values[check_ranks[i - 1]] - card_rank_values[check_ranks[i]] == 1:
                    count += 1
                    if check_ranks[i] == 'a':
                        best_straight_flush.append('A')
                    else:
                        best_straight_flush.append(check_ranks[i])
                else:
                    break

            if count > 3:
                best_straight_flush = best_straight_flush[0:5]

                filtered_cards = []
                for card in self.cards:
                    if card.rank in best_straight_flush:
                        filtered_cards.append(card)

                for suit in self.unique_suits:
                    count = 0
                    for card in filtered_cards:
                        if card.suit == suit:
                            count += 1

                    if count > 4:
                        self.suit = suit
                        self.ranks = best_straight_flush
                        return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for rank in self.ranks:
            for card in self.cards:
                if card.rank == rank and card.suit == self.suit:
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
        return "Straight Flush"

    def get_detailed_name(self):
        return "Straight Flush (" + self.suit + ", " + self.ranks[0] + ")"