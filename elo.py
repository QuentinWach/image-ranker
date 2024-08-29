class EloRanking:
    def __init__(self, k_factor=32, initial_rating=1400):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings = {}
        self.counts = {}
        self.upvotes = {}
        self.downvotes = {}

    def get_rating(self, player):
        return self.ratings.get(player, self.initial_rating)

    def update_elo(self, winner, loser):
        winner_rating = self.get_rating(winner)
        loser_rating = self.get_rating(loser)

        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 - expected_winner

        new_winner_rating = winner_rating + self.k_factor * (1 - expected_winner)
        new_loser_rating = loser_rating + self.k_factor * (0 - expected_loser)

        self.ratings[winner] = new_winner_rating
        self.ratings[loser] = new_loser_rating

        self.counts[winner] = self.counts.get(winner, 0) + 1
        self.counts[loser] = self.counts.get(loser, 0) + 1

        self.upvotes[winner] = self.upvotes.get(winner, 0) + 1
        self.downvotes[loser] = self.downvotes.get(loser, 0) + 1

    def get_rankings(self):
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)