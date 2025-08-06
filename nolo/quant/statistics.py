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


class OrnsteinUhlenbeckEstimator:
    """Fits an AR(1) / Ornstein-Uhlenbeck SDE to price series for statistical arbitrage & range trading."""

    @staticmethod
    def fit(prices: Sequence[float], window: int = 50) -> OUProcessState:
        n = len(prices)
        if n < 10:
            last = float(prices[-1]) if n > 0 else 0.0
            return OUProcessState(0.0, last, 0.0, 999.0, 0.0, False)
