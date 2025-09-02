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
            measurement_noise=self.config.kalman_measurement_noise,
        )
        self.smc = SmartMoneyAnalyzer()
        self._prev_regime: RegimeType = RegimeType.MIXED

    def detect(self, bars: Sequence[Bar]) -> RegimeState:
        n = len(bars)
        if n < 25:
            return RegimeState(
                regime=RegimeType.MIXED,
                confidence=0.35,
                hurst_exponent=0.5,
                efficiency_ratio=0.3,
                adx=15.0,
                bb_width_pct=1.0,
                atr_ratio=1.0,
                kalman_slope=0.0,
                entropy=0.5,
                structure_bias=MarketStructureBias.NEUTRAL,
                probabilities={r.value: 1.0 / 7.0 for r in RegimeType if r != RegimeType.MIXED},
            )

        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]

        # 1. Moving Averages & ADX
        fast_ma = IndicatorEngine.ema(closes, self.config.fast_ma_period)
        slow_ma = IndicatorEngine.ema(closes, self.config.slow_ma_period)
        trend_ma = IndicatorEngine.ema(closes, self.config.trend_ma_period)
        adx_vals, plus_di, minus_di = IndicatorEngine.adx(
            highs, lows, closes, self.config.adx_period
        )
