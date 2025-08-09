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

        theta = -math.log(max(1e-6, 1.0 + b))
        mu = -a / b
        residuals = [dx[i] - (a + b * x_prev[i]) for i in range(len(dx))]
        sigma = math.sqrt(sum(r * r for r in residuals) / max(1, len(residuals) - 1))
        half_life = math.log(2.0) / max(1e-6, theta)

        # Stationary standard deviation of OU process: sigma / sqrt(2 * theta)
        ou_std = sigma / math.sqrt(max(1e-9, 2.0 * theta))
        z_score = (sub[-1] - mu) / ou_std if ou_std > 1e-12 else 0.0
        is_mr = 1.5 <= half_life <= 45.0

        return OUProcessState(
            theta=theta,
            mu=mu,
            sigma=sigma,
            half_life_bars=half_life,
            z_score=z_score,
            is_mean_reverting=is_mr,
        )


class QuantitativeStatistics:
    """High-efficiency statistical estimators for volatility and cross-asset correlation."""

    @staticmethod
    def rolling_zscore(values: Sequence[float], window: int = 20) -> float:
        n = len(values)
        if n < 2:
            return 0.0
        sub = [float(x) for x in values[-min(n, window) :]]
        mean = sum(sub) / len(sub)
        var = sum((x - mean) ** 2 for x in sub) / len(sub)
        sd = math.sqrt(var)
        if sd <= 1e-12:
            return 0.0
        return (sub[-1] - mean) / sd

    @staticmethod
    def parkinson_volatility(
        highs: Sequence[float],
        lows: Sequence[float],
        window: int = 20,
    ) -> float:
        """High-Low range Parkinson volatility estimator (5x more efficient than close-to-close)."""
        n = min(len(highs), len(lows))
        if n == 0:
            return 0.0
        w = min(n, window)
        acc = 0.0
        for i in range(n - w, n):
            h = max(1e-9, float(highs[i]))
            l = max(1e-9, float(lows[i]))
            ratio = math.log(h / l) if h >= l else 0.0
            acc += ratio * ratio
        factor = 1.0 / (4.0 * w * math.log(2.0))
        return math.sqrt(max(0.0, factor * acc))

