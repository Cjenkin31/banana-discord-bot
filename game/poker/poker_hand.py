card_rank_values = {'a': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

class PokerHand:
    def __init__(self, value):
        self.hand_type_value = value

        self.cards = []
        self.unique_ranks = []
        self.unique_suits = []

    def makes_hand(self, hand):
        self.cards = sorted(hand, key=lambda card: card_rank_values[card.rank], reverse=True)
        self.unique_ranks = sorted({card.rank for card in self.cards},
                                   key=lambda rank: card_rank_values[rank], reverse=True)
        self.unique_suits = {card.suit for card in self.cards}

    def compare_hand(self, hand):
        if self.hand_type_value > hand.hand_type_value:
            return 1
        if self.hand_type_value < hand.hand_type_value:
            return -1
        return 0

    def compare_equal_type_hands(self, hand):
        bestCards = self.get_kickers()
        handBestCards = hand.get_kickers()

        limit = min(len(bestCards), len(handBestCards))

        for i in range(limit):
            if card_rank_values[bestCards[i].rank] > card_rank_values[handBestCards[i].rank]:
                return 1
            if card_rank_values[bestCards[i].rank] < card_rank_values[handBestCards[i].rank]:
                return -1

        return 0

    def get_hand_cards(self):
        raise Exception("Method 'get_hand_cards' must be implemented in concrete class")

    def get_kickers(self):
        kickers = []
        for card in self.cards:
            if card not in self.get_hand_cards():
                kickers.append(card)
        return kickers

    def get_ranked_cards(self):
        ranked_cards = self.get_hand_cards()
        available_cards = self.get_kickers()

        while len(ranked_cards) < 5 and available_cards:
            ranked_cards.append(available_cards.pop(0))

        return ranked_cards

    def get_name(self):
        raise Exception("Method 'get_name' must be implemented in concrete class")

    def get_detailed_name(self):
        raise Exception("Method 'get_detailed_name' must be implemented in concrete class")

    def __str__(self):
        return self.get_detailed_name() + " [ " + ", ".join(str(card) for card in self.cards) + " ]"