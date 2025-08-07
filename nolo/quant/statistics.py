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

        sub = [float(p) for p in prices[-min(n, window) :]]
        m = len(sub)
        x_prev = sub[:-1]
        dx = [sub[i] - sub[i - 1] for i in range(1, m)]

        mean_x = sum(x_prev) / len(x_prev)
        mean_dx = sum(dx) / len(dx)

        cov = sum((x_prev[i] - mean_x) * (dx[i] - mean_dx) for i in range(len(dx)))
        var_x = sum((x - mean_x) ** 2 for x in x_prev)

        if var_x <= 1e-14:
            return OUProcessState(0.0, mean_x, 0.0, 999.0, 0.0, False)

        # dx_t = a + b * x_{t-1} + eps_t, where b = -theta
        b = cov / var_x
        a = mean_dx - b * mean_x

        if b >= -1e-5 or b <= -1.95:
            # Non-stationary or explosive
            std_sub = math.sqrt(var_x / max(1, len(x_prev)))
            z = (sub[-1] - mean_x) / std_sub if std_sub > 1e-12 else 0.0
            return OUProcessState(0.0, mean_x, std_sub, 999.0, z, False)
