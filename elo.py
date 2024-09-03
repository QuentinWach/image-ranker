from trueskill import Rating, rate_1vs1

class TrueSkillRanking:
    def __init__(self, mu=0.0, sigma=8.33):
        self.mu = mu
        self.sigma = sigma
        self.ratings = {}
        self.counts = {}
        self.upvotes = {}
        self.downvotes = {}

    def get_rating(self, player):
        return self.ratings.get(player, Rating(mu=self.mu, sigma=self.sigma))

    def update_rating(self, winner, loser):
        winner_rating = self.get_rating(winner)
        loser_rating = self.get_rating(loser)

        new_winner_rating, new_loser_rating = rate_1vs1(winner_rating, loser_rating)

        self.ratings[winner] = new_winner_rating
        self.ratings[loser] = new_loser_rating

        self.counts[winner] = self.counts.get(winner, 0) + 1
        self.counts[loser] = self.counts.get(loser, 0) + 1

        self.upvotes[winner] = self.upvotes.get(winner, 0) + 1
        self.downvotes[loser] = self.downvotes.get(loser, 0) + 1

    def get_rankings(self):
        return sorted(self.ratings.items(), key=lambda x: x[1].mu, reverse=True)

    def get_uncertainty(self, player):
        rating = self.get_rating(player)
        return rating.sigma