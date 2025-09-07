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
