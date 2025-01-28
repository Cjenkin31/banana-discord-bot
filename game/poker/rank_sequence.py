from game.poker.poker_hand import PokerHand
from game.poker.poker_hand import card_rank_values

class RankSequence(PokerHand):
    def __init__(self, value, count, name="RankSequence"):
        super().__init__(value)
        self.count = count
        self.name = name
        self.ranks = []

    def makes_hand(self, hand):
        super().makes_hand(hand)

        check_ranks = self.unique_ranks.copy()

        if 'A' in check_ranks:
            check_ranks.append('a')

        for r in range(1, len(check_ranks)):
            best_sequence = [check_ranks[r - 1]]

            count = 0
            for i in range(r, len(check_ranks)):
                if card_rank_values[check_ranks[i - 1]] - card_rank_values[check_ranks[i]] == 1:
                    count += 1
                    if check_ranks[i] == 'a':
                        best_sequence.append('A')
                    else:
                        best_sequence.append(check_ranks[i])
                else:
                    break

            if count >= self.count - 1:
                self.ranks = best_sequence[0:self.count]
                return True

        return False

    def get_hand_cards(self):
        hand_cards = []
        for rank in self.ranks:
            for card in self.cards:
                if card.rank == rank:
                    hand_cards.append(card)
                    break
        return hand_cards

    def compare_equal_type_hands(self, hand):
        if card_rank_values[self.ranks[0]] > card_rank_values[hand.ranks[0]]:
            return 1
        if card_rank_values[self.ranks[0]] < card_rank_values[hand.ranks[0]]:
            return -1
        return super().compare_equal_type_hands(hand)

    def get_name(self):
        return self.name

    def get_detailed_name(self):
        return f"{self.name} ({self.ranks[0]})"