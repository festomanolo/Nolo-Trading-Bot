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
                cum_dev = []
                acc = 0.0
                for x in centered:
                    acc += x
                    cum_dev.append(acc)
                r = max(cum_dev) - min(cum_dev)
                variance = sum(x * x for x in centered) / w
                s = math.sqrt(variance)
                if s > 1e-12 and r > 0:
                    rs_vals.append(r / s)
            if rs_vals:
                avg_rs = sum(rs_vals) / len(rs_vals)
                if avg_rs > 0:
                    log_sizes.append(math.log(w))
                    log_rs.append(math.log(avg_rs))

        if len(log_sizes) < 2:
            return HurstAnalyzer._single_scale_hurst(returns)

        # Ordinary Least Squares slope of log(R/S) vs log(n)
        k = len(log_sizes)
        mean_x = sum(log_sizes) / k
        mean_y = sum(log_rs) / k
        num = sum((log_sizes[i] - mean_x) * (log_rs[i] - mean_y) for i in range(k))
        den = sum((log_sizes[i] - mean_x) ** 2 for i in range(k))
        if den <= 1e-12:
            return 0.5

        h = num / den
        return max(0.05, min(0.95, h))

    @staticmethod
    def _single_scale_hurst(returns: Sequence[float]) -> float:
        m = len(returns)
        if m < 4:
            return 0.5
        mean_val = sum(returns) / m
        centered = [x - mean_val for x in returns]
        acc = 0.0
        cum = []
        for x in centered:
            acc += x
            cum.append(acc)
        r = max(cum) - min(cum)
        s = math.sqrt(sum(x * x for x in centered) / m)
        if s <= 1e-12 or r <= 0:
            return 0.5
        h = math.log(r / s) / math.log(m)
        return max(0.05, min(0.95, h))

    @staticmethod
    def fractal_dimension(prices: Sequence[float]) -> float:
        """Compute Fractal Dimension D = 2 - H."""
        return 2.0 - HurstAnalyzer.compute_hurst(prices)

    @staticmethod
    def variance_ratio(prices: Sequence[float], lag: int = 4) -> float:
        """
        Lo-MacKinlay Variance Ratio VR(q) = Var(r_t(q)) / (q * Var(r_t(1))).
        VR > 1 implies positive autocorrelation (trending); VR < 1 implies mean reversion.
        """
        n = len(prices)
        if n <= lag + 4 or lag < 2:
            return 1.0
        log_p = [math.log(max(1e-9, float(p))) for p in prices]
        r1 = [log_p[i] - log_p[i - 1] for i in range(1, n)]
        rq = [log_p[i] - log_p[i - lag] for i in range(lag, n)]

        mean1 = sum(r1) / len(r1)
        var1 = sum((x - mean1) ** 2 for x in r1) / max(1, len(r1) - 1)
        if var1 <= 1e-14:
            return 1.0

        meanq = sum(rq) / len(rq)
        varq = sum((x - meanq) ** 2 for x in rq) / max(1, len(rq) - 1)
        return max(0.1, min(3.0, varq / (lag * var1)))
