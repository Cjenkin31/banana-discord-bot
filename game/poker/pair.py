from game.poker.rank_match import RankMatch

class Pair(RankMatch):
    def __init__(self, value):
        super().__init__(value, 2, "Pair")