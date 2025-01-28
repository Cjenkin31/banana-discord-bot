from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class SuitMatch(PokerHand):
    def __init__(self, value, count, name="SuitMatch"):
        super().__init__(value)
        self.count = count
        self.name = name
        self.suit = None

    def makes_hand(self, hand):
        super().makes_hand(hand)

        for suit in self.unique_suits:
            count = 0
            for card in self.cards:
                if card.suit == suit:
                    count += 1

            if count >= self.count:
                self.suit = suit
                return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for card in self.cards:
            if len(hand_cards) == self.count:
                break
            if card.suit == self.suit:
                hand_cards.append(card)
        return hand_cards

    def compare_equal_type_hands(self, hand):
        best_cards = self.get_hand_cards()
        hand_best_cards = hand.get_hand_cards()

        limit = len(best_cards) if len(best_cards) <= len(hand_best_cards) else len(hand_best_cards)

        for i in range(limit):
            if card_rank_values[best_cards[i].rank] > card_rank_values[hand_best_cards[i].rank]:
                return 1
            if card_rank_values[best_cards[i].rank] < card_rank_values[hand_best_cards[i].rank]:
                return -1

        return super().compare_equal_type_hands(hand)

    def get_name(self):
        return self.name

    def get_detailed_name(self):
        return f"{self.name} ({self.suit}, {self.get_hand_cards()[0].rank})"