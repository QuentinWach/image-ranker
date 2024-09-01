<div align="center">
  <h1>Image Ranker</h1>
  <p>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/github/license/QuentinWach/image-ranker" alt="License">
    </a>
    <a href="https://github.com/QuentinWach/1v1-image-ranker/stargazers">
      <img src="https://img.shields.io/github/stars/QuentinWach/image-ranker" alt="GitHub stars">
    </a>
    <a href="https://github.com/QuentinWach/1v1-image-ranker/commits/main">
      <img src="https://img.shields.io/github/last-commit/QuentinWach/image-ranker" alt="Last update">
    </a>
  </p>
</div>

![alt text](static/header.png)

## Core Features
- **TrueSkill ELO algorithm.** An advanced algorithm that takes into account the uncertainty in the ratings and updates the ranks **globally** after each comparison since if A > B and B > C then we can infer that A > C. This achieves accurate results much faster than a typical ELO algorithm.
- **Web GUI for easy use.**
- **Select images from a local directory without needing to upload or move them.**
- **Export ranking data as .csv.**

<!--
## Additional Features
- **Eliminate images from the ranking process for even faster results.**


- **Import corresponding text-prompts for each image.**
- **Change the ELO algorithm's parameters.**
-->
## 🚀 Installation & Usage
1. Clone the repository:
   ```
   git clone https://github.com/QuentinWach/image-ranker.git
   cd image-ranker
   ```
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```
   pip install flask trueskill
   ```
4. Run the Flask app: `python app.py`.
5. Open a web browser and navigate to `http://localhost:5000`.

---
## TrueSkill ELO: How Does It Work?
Each image is represented by two values:
- μ (mu): The estimated "skill" level.
- σ (sigma): The uncertainty in that estimate.

New items start with a default μ (often 25) and high σ (often 8.33). When two items are compared, their μ and σ values are used to calculate the expected outcome. The actual outcome is compared to this expectation. The winner's μ increases, the loser's decreases.Both items' σ typically decreases (representing increased certainty). The magnitude of changes depends on:
- How surprising the outcome was (based on current ratings).
- The current uncertainty (σ) of each item.

It uses Gaussian distributions to model skill levels and employs factor graphs and message passing for efficient updates. Items are typically ranked by their μ - 3σ (a conservative estimate).

Importantly, the algorithm updates all previously ranked items simultaneously with every comparison, rather than updating only the new images. This means that the algorithm can take into account all of the information available from the comparisons, rather than just the pairwise comparisons.

Thus, overall, this system allows for efficient ranking with incomplete comparison data, making it well-suited for large sets of items where exhaustive pairwise comparisons are impractical!

## Why? Reinforcement Learning with Human Feedback (RLHF)
Post-training foundation models is what makes them actually useful. For example, large language models may not even chat with you without post-training. The same is true for images. In order to do so, a common technique is RLHF, which uses a reward model to reward or punish the output of the generative foundation model based on user preferences. In order to create this reward model, we need to know the user preferences which requires a dataset, here images. So whether it is to make some radical changes to an already existing model like Stable Diffusion or Flux, or to train your own model, it is important to be able to rank the images somehow to know which images are better. This is where this app comes in.

## What's Next?
Once you have a dataset of images, you can use this app to rank them. You can then use the ranked dataset to train your reward model. Which you can then use to fine-tune your generative model. You might want to look into the following:
+ [Transformer Reinforcement Learning (TRL) (huggingface.co)](https://huggingface.co/docs/trl/main/en/index): TRL is a library for training language models using reinforcement learning techniques. It provides tools and utilities to implement RLHF and other RL algorithms for fine-tuning language models based on human preferences or other reward signals.
+ [PEFT (Parameter-Efficient Fine-Tuning) (huggingface.co)](https://huggingface.co/blog/trl-peft): PEFT is a technique to fine-tune language models using only a small subset of the model's parameters, making it much more efficient than full-parameter fine-tuning.
+ [Reward Model Training (medium.com)](https://medium.com/towards-generative-ai/reward-model-training-2209d1befb5f): This article provides a comprehensive guide to training a reward model for language models.
+ [RLHF for LLMs (superannotate.com)](https://www.superannotate.com/blog/rlhf-for-llm)
+ [RLHF (labellerr.com)](https://www.labellerr.com/blog/reinforcement-learning-from-human-feedback/)



<!--
## ELO: How Does It Work?
The typical ELO algorithm can be used to rank images based on pairwise comparisons. Here's how it works:

1. **Initialization**: 
   - Each image starts with an initial rating (default: 1400).
   - A K-factor (default: 32) determines the maximum change in rating after each comparison.

2. **Rating Calculation**:
   - When two images are compared, their current ratings are used to calculate the expected outcome.
   - The formula for expected score is: 1 / (1 + 10^((opponent_rating - player_rating) / 400))

3. **Rating Update**:
   - After each comparison, the ratings of both images are updated.
   - The winner's rating increases, and the loser's rating decreases.
   - The amount of change depends on the expected outcome and the actual outcome.
   - New Rating = Old Rating + K * (Actual Outcome - Expected Outcome)
     - Actual Outcome is 1 for the winner and 0 for the loser.

4. **Tracking Statistics**:
   - The system keeps track of the number of comparisons for each image.
   - It also counts upvotes (wins) and downvotes (losses) for each image.
   - Ensures that each image is compared against every other image exactly once which is necessary for the algorithm to converge. (Shown as a progress bar in the web app.)

5. **Ranking**:
   - Images are ranked based on their current ELO rating.
   - The `get_rankings()` method returns a sorted list of images by their ratings.

This implementation ensures that images consistently chosen as better will rise in the rankings, while those consistently chosen as worse will fall. The system is self-correcting and allows for dynamic changes in rankings as more comparisons are made.

-->