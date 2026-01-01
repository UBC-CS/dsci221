# Lab 1: Timing Experiments

## Planning Notes

### Core idea
Students predict, measure, and explain running times. Build intuition for Big-O before the formal definition.

### Puzzle from lecture (moved here)
**The crossover problem:**

Suppose we have two ways to solve a problem:
- **Method A**: O(n) but slow per operation (1 ms each)
- **Method B**: O(n²) but fast per operation (0.001 ms each)

| n | Method A (n × 1ms) | Method B (n² × 0.001ms) |
|---|---|---|
| 10 | 10 ms | 0.1 ms |
| 100 | 100 ms | 10 ms |
| 1,000 | 1,000 ms | 1,000 ms |
| 10,000 | 10,000 ms | 100,000 ms |

At n = 1,000, they cross over. Beyond that, the "slower" O(n) algorithm wins.

**Key insight:** Big-O dominates eventually, but constants matter for small n.

### Other potential exercises

1. **Predict then measure**: Given code snippets, predict relative speeds, then time them
2. **Identify the loop**: Look at nested vs single loops, predict O(n) vs O(n²)
3. **pandas operations**: Time vectorized vs iterrows on increasing data sizes
4. **Plot your results**: Generate timing data, plot, identify the curve shape

### Tools needed
- `time` module or `%%timeit` magic
- matplotlib for plotting
- pandas for the DataFrame exercises

### Connection to lecture
- Builds on Shazam mystery, pizza delivery example
- Reinforces "it depends" → specifically depends on n
- Prepares for formal Big-O definition on Tuesday
