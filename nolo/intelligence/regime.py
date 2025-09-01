"""
Multi-Factor Bayesian & Markov Regime Detection Engine.

Combines 7 orthogonal quantitative dimensions:
1. Hurst Exponent H (fractal persistence vs mean reversion)
2. Kaufman Efficiency Ratio ER (directional efficiency vs path noise)
3. Wilder's ADX & Directional Indicators (+DI / -DI)
4. Bollinger Bandwidth & ATR Expansion Ratio
5. 2D Kalman Filter Velocity & Slope
6. Shannon Return Entropy
7. Institutional Market Structure (BOS / CHoCH / Liquidity Sweep)
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from nolo.config import IndicatorConfig
from nolo.microstructure.smc import SmartMoneyAnalyzer
from nolo.quant.entropy import MarketEntropy
from nolo.quant.hurst import HurstAnalyzer
from nolo.quant.indicators import IndicatorEngine
from nolo.quant.kalman import KalmanTrendTracker
from nolo.types import Bar, MarketStructureBias, RegimeState, RegimeType


class AdaptiveRegimeEngine:
    """Classifies real-time market state into 7 distinct institutional regimes with posterior probabilities."""

    def __init__(self, config: Optional[IndicatorConfig] = None) -> None:
        self.config = config or IndicatorConfig()
        self.kalman = KalmanTrendTracker(
            process_noise=self.config.kalman_process_noise,
