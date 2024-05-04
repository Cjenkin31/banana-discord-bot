from game.poker.rank_match import RankMatch

class FourOfAKind(RankMatch):
    def __init__(self, value):
        super().__init__(value, 4, "Four Of A Kind")