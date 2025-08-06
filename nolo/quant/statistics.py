"""
Statistical Estimators: Ornstein-Uhlenbeck Mean-Reversion Process, Z-Scores,
Parkinson/Garman-Klass High-Frequency Volatility, and Rolling Correlation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class OUProcessState:
    """Parameters of a fitted Ornstein-Uhlenbeck mean-reverting process dX_t = theta*(mu - X_t)dt + sigma*dW_t."""

    theta: float
    mu: float
    sigma: float
    half_life_bars: float
    z_score: float
    is_mean_reverting: bool


