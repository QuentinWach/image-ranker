# ToDo
+ [ ] Host the app on a website
  + https://1v1rank.com
  + https://1v1.lol
  + https://1v1.fun
  + https://paircompare.com
  + https://imageranker.com
  + https://imagecompare.com
+ [ ] Add a footer to the app
+ [ ] Show folder name after importing images
+ [ ] Add a "Made with ❤️ by Quentin" footer to the app and linking to my Twitter
+ [ ] Add a "Tweet" button to the app
+ [ ] Add Google Ads pop up ad every 10 images
+ [ ] Add an Google Ads ad between the ranking images every 15 images
+ [ ] Add option to turn off ads by logging in with Google and paying a small one-time fee
+ [ ] Add Google Analytics to the app
+ [ ] Improve the performance of the app, showing only the top 10 and bottom 10 images in the ranking.


---
## Advanced Techniques
- **Rank Matrix Factorisation (RMF)**: This is a more sophisticated approach to analyze and decompose rank matrices. RMF aims to find underlying patterns in ranking data, providing insights into the rankings that form the basis of the data.
- **Nuclear Norm Minimization**: This technique is used for rank aggregation, especially when dealing with incomplete or noisy data. It involves finding a low-rank approximation of the pairwise comparison matrix.
- **Hodge Decomposition**: This is an algorithm used for global ranking based on pairwise comparisons. It can be enhanced with matrix completion techniques to improve results when there are limited pairwise comparisons available.

- **Adaptive Sampling**: To efficiently rank images pairwise with high accuracy without comparing every image to every other image, you can use a technique called "adaptive sampling" or "active learning." Here's a concise approach:
   1. Start with a random subset of pairwise comparisons.
   2. Use these initial comparisons to create a preliminary ranking.
   3. Employ an algorithm like TrueSkill or Bradley-Terry-Luce (BTL) model to estimate image rankings and uncertainties.
   4. Adaptively select the next pair to compare:
      - Choose pairs with high uncertainty
      - Focus on closely ranked images
      - Occasionally compare distant pairs to refine overall ranking
   5. Update rankings after each comparison.
   6. Repeat steps 4-5 until desired accuracy or budget is reached.

## Future
+ [ ] Train a neural network to predict if an image is better than another image.

