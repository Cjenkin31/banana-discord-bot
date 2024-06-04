from game.poker.rank_match import RankMatch

class ThreeOfAKind(RankMatch):
    def __init__(self, value):
        super().__init__(value, 3, "Three Of A Kind")