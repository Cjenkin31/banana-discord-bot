from game.poker.rank_sequence import RankSequence
from game.poker.poker_hand import card_rank_values

class StraightFlush(RankSequence):
    def __init__(self, value):
        super().__init__(value, 5, "Straight Flush")
        
    def makes_hand(self, hand):
        if super().makes_hand(hand):
            filtered_cards = []
            for card in self.cards:
                if card.rank in self.ranks:
                    filtered_cards.append(card)

            for suit in self.unique_suits:
                count = 0
                for card in filtered_cards:
                    if card.suit == suit:
                        count += 1

                if count >= self.count:
                    self.suit = suit
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

    def get_detailed_name(self):
        return f"{self.name} ({self.suit}, {self.ranks[0]})"