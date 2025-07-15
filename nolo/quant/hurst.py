"""
Hurst Exponent (Rescaled Range R/S & Variance Ratio) and Fractal Dimension analyzer.

Interpretation of Hurst Exponent H in [0, 1]:
- H > 0.55: Persistent trending series (positive long-memory autocorrelation)
- H ~ 0.50: Geometric Brownian Motion / Random walk
- H < 0.45: Anti-persistent / Mean-reverting series
Fractal Dimension D = 2.0 - H.
"""

from __future__ import annotations

import math
from typing import Sequence


class HurstAnalyzer:
    """Computes rolling Hurst Exponent, Fractal Dimension, and Variance Ratio."""

    @staticmethod
    def compute_hurst(prices: Sequence[float], min_chunk: int = 8) -> float:
        """
        Estimate the Hurst exponent using multi-scale Rescaled Range (R/S) regression.
        """
        n = len(prices)
