"""
Institutional Position Sizing Engine.

Implements:
- FIXED: Fixed fractional risk percentage per trade
- KELLY: Classic Kelly Criterion f* = (p - (1 - p) / b) * kelly_fraction
- ADAPTIVE_KELLY: Streak-adjusted Kelly Criterion
- BAYESIAN_KELLY: Beta-Bernoulli posterior win-rate blended with Neural Scorer probability
