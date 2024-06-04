from game.poker.rank_sequence import RankSequence

class Straight(RankSequence):
    def __init__(self, value):
        super().__init__(value, 5, "Straight")