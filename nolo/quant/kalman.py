"""
State-space 2D Kalman Filter for zero-lag price level, velocity, and innovation tracking.

Models price evolution as a continuous-time kinematic system:
    x_t = [price_t, velocity_t]^T
with adaptive measurement noise covariance R scaled by recent volatility shocks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass(frozen=True)
class KalmanState:
    """Snapshot of the Kalman state vector and uncertainty."""

    level: float
    velocity: float
    innovation: float
    innovation_std: float
    kalman_gain_level: float
    kalman_gain_velocity: float

    @property
    def z_score(self) -> float:
        if self.innovation_std <= 1e-12:
            return 0.0
        return self.innovation / self.innovation_std


class KalmanTrendTracker:
    """
    2-State Kinematic Kalman Filter tracking latent price level and trend velocity.

    State transition matrix F = [[1, dt], [0, 1]]
    Observation matrix      H = [1, 0]
    """

    def __init__(
        self,
        process_noise: float = 1e-4,
        measurement_noise: float = 1e-2,
        adaptive_noise: bool = True,
    ) -> None:
        self.q = max(1e-9, process_noise)
        self.r_base = max(1e-9, measurement_noise)
        self.adaptive_noise = adaptive_noise
