from game.poker.straight_flush import StraightFlush

class RoyalFlush(StraightFlush):
    def makes_hand(self, hand):
        super().makes_hand(hand)

        return self.ranks[0] == 'A'

    def get_hand_cards(self):
        return super().get_hand_cards()

    def compare_equal_type_hands(self, hand):
        return super().compare_equal_type_hands(hand)

    def get_name(self):
        return "Royal Flush"

    def get_detailed_name(self):
        return "Royal Flush (" + self.suit + ")"