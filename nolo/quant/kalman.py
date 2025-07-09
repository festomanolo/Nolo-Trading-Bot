"""
State-space 2D Kalman Filter for zero-lag price level, velocity, and innovation tracking.

Models price evolution as a continuous-time kinematic system:
    x_t = [price_t, velocity_t]^T
with adaptive measurement noise covariance R scaled by recent volatility shocks.
"""

