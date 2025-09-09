"""
Online Adaptive Neural & Logistic Ensemble Signal Scorer.

Combines:
1. Calibrated Domain Expert Prior Weights across 12 normalized quantitative features
2. Online 2-Layer Neural Perceptron with LeakyReLU hidden activations & L2 weight decay
3. Exponentially weighted online updates (`partial_fit`) from realized trade outcomes
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from nolo.config import MLConfig

FEATURE_NAMES: List[str] = [
    "trend_alignment",       # [-1, +1] MTF EMA + SuperTrend + Ichimoku alignment
    "kalman_velocity",       # [-1, +1] normalized Kalman velocity in signal direction
    "hurst_persistence",     # [-1, +1] Hurst regime match for strategy type
    "efficiency_ratio",      # [0, 1] Kaufman efficiency ratio
    "adx_strength",          # [0, 1] normalized ADX trend strength
    "rsi_confluence",        # [0, 1] RSI non-exhaustion / reversal quality
    "macd_impulse",          # [-1, +1] MACD histogram acceleration in trade direction
    "smc_zone_confluence",   # [0, 1] Order Block / FVG / Sweep alignment
    "orderflow_pressure",    # [-1, +1] CVD & intrabar buying/selling pressure
    "currency_divergence",   # [-1, +1] G8 Currency Strength divergence support
    "htf_confirmation",      # [-1, +1] Higher timeframe trend agreement
    "volatility_quality",    # [0, 1] ATR expansion without spread toxicity
]


class AdaptiveNeuralScorer:
    """
    Hybrid Prior + Online Neural Signal Scorer.
    Outputs calibrated win probability P(win) in [0.05, 0.95].
    """

    def __init__(self, config: Optional[MLConfig] = None) -> None:
        self.config = config or MLConfig()
        # Domain-calibrated institutional base weights
        self.weights: Dict[str, float] = {
            "trend_alignment": 0.24,
            "kalman_velocity": 0.18,
            "hurst_persistence": 0.15,
            "efficiency_ratio": 0.14,
            "adx_strength": 0.12,
            "rsi_confluence": 0.14,
            "macd_impulse": 0.13,
            "smc_zone_confluence": 0.22,
            "orderflow_pressure": 0.18,
            "currency_divergence": 0.15,
            "htf_confirmation": 0.22,
            "volatility_quality": 0.12,
        }
        self.bias: float = -0.25
        self.samples_seen: int = 0
        self.ewma_accuracy: float = 0.60

        # Second-order non-linear interaction terms (SMC * OrderFlow, Trend * HTF, Kalman * Hurst)
        self.interaction_weights: Dict[str, float] = {
            "trend_x_htf": 0.15,
            "smc_x_orderflow": 0.18,
            "kalman_x_hurst": 0.12,
        }

    @staticmethod
    def _sigmoid(z: float) -> float:
        z_clamped = max(-15.0, min(15.0, z))
        return 1.0 / (1.0 + math.exp(-z_clamped))

    @staticmethod
    def _leaky_relu(x: float) -> float:
        return x if x >= 0.0 else 0.15 * x

    def predict_probability(self, features: Dict[str, float]) -> float:
        """Compute calibrated probability of trade success given normalized feature vector."""
        linear_z = self.bias
        for name in FEATURE_NAMES:
            val = max(-2.0, min(2.0, float(features.get(name, 0.0))))
            linear_z += self.weights.get(name, 0.0) * val

        # Non-linear hidden layer interactions
