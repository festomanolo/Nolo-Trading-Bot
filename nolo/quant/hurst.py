"""
Hurst Exponent (Rescaled Range R/S & Variance Ratio) and Fractal Dimension analyzer.

Interpretation of Hurst Exponent H in [0, 1]:
- H > 0.55: Persistent trending series (positive long-memory autocorrelation)
- H ~ 0.50: Geometric Brownian Motion / Random walk
- H < 0.45: Anti-persistent / Mean-reverting series
Fractal Dimension D = 2.0 - H.
