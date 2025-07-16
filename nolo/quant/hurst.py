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
        if n < 20:
            return 0.5

        returns = []
        for i in range(1, n):
            p0 = max(1e-9, float(prices[i - 1]))
            p1 = max(1e-9, float(prices[i]))
            returns.append(math.log(p1 / p0))

        m = len(returns)
        chunk_sizes = []
        size = max(min_chunk, 8)
        while size <= m:
            chunk_sizes.append(size)
            size = int(size * 1.6)
        if chunk_sizes and chunk_sizes[-1] != m and m >= min_chunk:
            chunk_sizes.append(m)

        if len(chunk_sizes) < 2:
            return HurstAnalyzer._single_scale_hurst(returns)

        log_sizes = []
        log_rs = []

        for w in chunk_sizes:
            num_chunks = m // w
            if num_chunks < 1:
                continue
            rs_vals = []
            for c in range(num_chunks):
                sub = returns[c * w : (c + 1) * w]
                mean_val = sum(sub) / w
                centered = [x - mean_val for x in sub]
