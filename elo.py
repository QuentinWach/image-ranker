from trueskill import Rating, rate_1vs1

class TrueSkillRanking:
    def __init__(self, mu=0.0, sigma=8.33):
        self.mu = mu
        self.sigma = sigma
        self.ratings = {}
        self.counts = {}
        self.upvotes = {}
        self.downvotes = {}
        self.comparison_history = []

    def get_rating(self, player):
        return self.ratings.get(player, Rating(mu=self.mu, sigma=self.sigma))

    def update_rating(self, comparisons):
        if isinstance(comparisons, tuple):
            comparisons = {comparisons}

        for winner, loser in comparisons:
            winner_rating = self.get_rating(winner)
            loser_rating = self.get_rating(loser)

            new_winner_rating, new_loser_rating = rate_1vs1(winner_rating, loser_rating)

            self.ratings[winner] = new_winner_rating
            self.ratings[loser] = new_loser_rating

            self.counts[winner] = self.counts.get(winner, 0) + 1
            self.counts[loser] = self.counts.get(loser, 0) + 1

            self.upvotes[winner] = self.upvotes.get(winner, 0) + 1
            self.downvotes[loser] = self.downvotes.get(loser, 0) + 1

        self.comparison_history.extend(comparisons)        
        
    def recalculate_rankings(self):
        self.ratings = {}
        self.counts = {}
        self.upvotes = {}
        self.downvotes = {}

        comparisons_to_process = self.comparison_history[:]
        self.comparison_history = []

        for winner, loser in comparisons_to_process:
            if winner is None:  # Remove loser from ratings when winner is None
                if loser in self.ratings:
                    del self.ratings[loser]
                if loser in self.counts:
                    del self.counts[loser]
                if loser in self.upvotes:
                    del self.upvotes[loser]
                if loser in self.downvotes:
                    del self.downvotes[loser]
                self.comparison_history.append((winner, loser))
            else:
                self.update_rating((winner, loser))
            
    def remove_image(self, images):
        if isinstance(images, str):
            images_to_remove = {images}
        else:
            images_to_remove = set(images)
        self.comparison_history = [(winner, loser) for winner, loser in self.comparison_history if not (winner is not None and (winner in images_to_remove or loser in images_to_remove))]
        self.comparison_history.extend([(None, img) for img in images_to_remove])  # Add the removed images to the comparison history
        self.recalculate_rankings()

    def get_rankings(self):
        return sorted(self.ratings.items(), key=lambda x: x[1].mu, reverse=True)

    def get_uncertainty(self, player):
        rating = self.get_rating(player)
        return rating.sigma