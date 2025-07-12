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
        self.reset()

    def reset(self) -> None:
        self._initialized = False
        self.level = 0.0
        self.velocity = 0.0
        # 2x2 state covariance matrix P
        self.p00 = 1.0
        self.p01 = 0.0
        self.p10 = 0.0
        self.p11 = 1.0
        self._ewma_innov_sq = self.r_base

    def update(self, measurement: float, dt: float = 1.0) -> KalmanState:
        """Process a single price observation and return updated Kalman state."""
        if not self._initialized:
            self.level = float(measurement)
            self.velocity = 0.0
            self.p00 = self.r_base
            self.p01 = 0.0
            self.p10 = 0.0
            self.p11 = self.q
            self._initialized = True
            return KalmanState(
                level=self.level,
                velocity=0.0,
                innovation=0.0,
                innovation_std=self.r_base**0.5,
                kalman_gain_level=1.0,
                kalman_gain_velocity=0.0,
            )

        # 1. Predict step: x_{k|k-1} = F x_{k-1|k-1}
        pred_level = self.level + self.velocity * dt
        pred_vel = self.velocity

        # Predict covariance: P_{k|k-1} = F P F^T + Q
        dt2 = dt * dt
        dt3 = dt2 * dt * 0.5
        dt4 = dt2 * dt2 * 0.25

        q00 = self.q * dt4
        q01 = self.q * dt3
        q11 = self.q * dt2

        p00_pred = self.p00 + dt * (self.p10 + self.p01) + dt2 * self.p11 + q00
        p01_pred = self.p01 + dt * self.p11 + q01
        p10_pred = self.p10 + dt * self.p11 + q01
        p11_pred = self.p11 + q11
