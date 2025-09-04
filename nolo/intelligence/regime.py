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

        # 2. Volatility & Bollinger Bandwidth
        atr_vals = IndicatorEngine.atr(highs, lows, closes, self.config.atr_period)
        curr_atr = max(1e-9, atr_vals[-1])
        avg_atr = sum(atr_vals[-20:]) / min(20, len(atr_vals))
        atr_ratio = curr_atr / max(1e-9, avg_atr)

        bb_up, _, bb_low = IndicatorEngine.bollinger_bands(
            closes, self.config.bollinger_period, self.config.bollinger_std
        )
        curr_close = max(1e-9, closes[-1])
        bb_width_pct = ((bb_up[-1] - bb_low[-1]) / curr_close) * 100.0

        # 3. Hurst Exponent & Entropy & Efficiency Ratio
        hurst_win = closes[-min(n, self.config.hurst_window) :]
        hurst = HurstAnalyzer.compute_hurst(hurst_win)
        er = MarketEntropy.efficiency_ratio(closes, period=14)
        entropy = MarketEntropy.shannon_entropy(closes[-30:])

        # 4. Kalman Velocity normalized by ATR
        k_states = self.kalman.filter_series(closes[-35:])
        kalman_slope = k_states[-1].velocity / curr_atr

        # 5. Smart Money Structure
        smc_snap = self.smc.analyze(bars)

        # Score each candidate regime
        adx_now = adx_vals[-1]
        ma_bull = fast_ma[-1] > slow_ma[-1] and closes[-1] > trend_ma[-1]
        ma_bear = fast_ma[-1] < slow_ma[-1] and closes[-1] < trend_ma[-1]
        recent_hh = closes[-1] > max(highs[-15:-1])
        recent_ll = closes[-1] < min(lows[-15:-1])

        scores: Dict[RegimeType, float] = {
            RegimeType.TREND_UP: 0.10,
            RegimeType.TREND_DOWN: 0.10,
            RegimeType.RANGE: 0.10,
            RegimeType.BREAKOUT_UP: 0.05,
            RegimeType.BREAKOUT_DOWN: 0.05,
            RegimeType.VOLATILITY: 0.05,
            RegimeType.LIQUIDITY_SWEEP: 0.05,
        }
