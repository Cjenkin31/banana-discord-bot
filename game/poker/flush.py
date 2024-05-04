
from game.poker.suit_match import SuitMatch

class Flush(SuitMatch):
    def __init__(self, value):
        super().__init__(value, 5, "Flush")