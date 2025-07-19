"""
Information-theoretic market entropy, Kaufman Efficiency Ratio, and Choppiness Index.

Used to distinguish structured directional impulse moves from high-entropy random noise.
"""

from __future__ import annotations

import math
from typing import Sequence


class MarketEntropy:
    """Calculates Shannon Entropy of return distributions, Kaufman ER, and Choppiness Index."""

