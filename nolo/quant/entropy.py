"""
Information-theoretic market entropy, Kaufman Efficiency Ratio, and Choppiness Index.

Used to distinguish structured directional impulse moves from high-entropy random noise.
"""

from __future__ import annotations

import math
from typing import Sequence


class MarketEntropy:
    """Calculates Shannon Entropy of return distributions, Kaufman ER, and Choppiness Index."""

    @staticmethod
    def shannon_entropy(prices: Sequence[float], bins: int = 8) -> float:
        """
        Normalized Shannon entropy in [0, 1] of price changes.
        Values near 1.0 indicate noisy, uniform disorder; lower values indicate structured regime.
        """
        n = len(prices)
        if n < 10 or bins < 2:
            return 0.5

        diffs = [float(prices[i]) - float(prices[i - 1]) for i in range(1, n)]
        lo = min(diffs)
        hi = max(diffs)
        span = hi - lo
        if span <= 1e-12:
            return 0.0

        counts = [0] * bins
        for d in diffs:
            idx = int(((d - lo) / span) * (bins - 1))
            idx = max(0, min(bins - 1, idx))
            counts[idx] += 1

        total = len(diffs)
        ent = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                ent -= p * math.log(p)

        max_ent = math.log(bins)
        return min(1.0, max(0.0, ent / max_ent)) if max_ent > 0 else 0.5
