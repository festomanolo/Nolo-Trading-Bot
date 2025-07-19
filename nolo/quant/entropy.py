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
