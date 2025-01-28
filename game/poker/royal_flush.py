from game.poker.straight_flush import StraightFlush

class RoyalFlush(StraightFlush):
    def __init__(self, value):
        super(StraightFlush, self).__init__(value, 5, "Royal Flush")

    def makes_hand(self, hand):
        if super().makes_hand(hand):
            return self.ranks[0] == 'A'
        return False

    def get_detailed_name(self):
        return f"{self.name} ({self.suit})"