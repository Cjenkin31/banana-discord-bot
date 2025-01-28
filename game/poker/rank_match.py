from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class RankMatch(PokerHand):
    def __init__(self, value, count, name="RankMatch"):
        super().__init__(value)
        self.count = count
        self.name = name
        self.rank = None

    def makes_hand(self, hand):
        super().makes_hand(hand)

        for rank in self.unique_ranks:
            count = 0
            for card in self.cards:
                if card.rank == rank:
                    count += 1

            if count == self.count:
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
        if card_rank_values[self.rank] < card_rank_values[hand.rank]:
            return -1
        return super().compare_equal_type_hands(hand)

    def get_name(self):
        return self.name

    def get_detailed_name(self):
        return f"{self.name} ({self.rank})"