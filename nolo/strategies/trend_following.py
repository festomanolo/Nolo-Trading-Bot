"""
Kalman + SuperTrend + Ichimoku Cloud Multi-Timeframe Trend Following Strategy.

Upgrades the v3.5 Trend Following logic with:
- State-space Kalman velocity confirmation
- Fixed SuperTrend band ratcheting
- Ichimoku Kumo Cloud + Tenkan/Kijun cross boost
- Order Flow Cumulative Volume Delta (CVD) alignment
"""

from __future__ import annotations

from typing import Dict, List, Optional

from nolo.quant.indicators import IndicatorEngine
from nolo.strategies.base import BaseStrategy, StrategyContext
from nolo.types import OrderSide, Signal


class KalmanTrendStrategy(BaseStrategy):
    """Institutional trend-following alpha engine."""

    name = "KalmanTrendFollowing"

    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        bars = ctx.bars
        if len(bars) < 55:
            return None

        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        ind_cfg = self.config.indicators

        fast_ma = IndicatorEngine.ema(closes, ind_cfg.fast_ma_period)
        slow_ma = IndicatorEngine.ema(closes, ind_cfg.slow_ma_period)
        rsi_vals = IndicatorEngine.rsi(closes, ind_cfg.rsi_period)
        macd_main, macd_sig, macd_hist = IndicatorEngine.macd(
            closes, ind_cfg.macd_fast, ind_cfg.macd_slow, ind_cfg.macd_signal
        )
        atr_vals = IndicatorEngine.atr(highs, lows, closes, ind_cfg.atr_period)
        _, st_dir = IndicatorEngine.supertrend(
            highs, lows, closes, ind_cfg.atr_period, ind_cfg.supertrend_mult
        )
        ichi = IndicatorEngine.ichimoku(
            highs, lows, ind_cfg.ichimoku_tenkan, ind_cfg.ichimoku_kijun, ind_cfg.ichimoku_senkou_b
        )

        curr_close = closes[-1]
        curr_atr = max(1e-9, atr_vals[-1])

        buy_core = (
            fast_ma[-1] > slow_ma[-1]
            and fast_ma[-2] >= slow_ma[-2] * 0.9998
            and macd_main[-1] > macd_sig[-1]
            and st_dir[-1] > 0
            and 40.0 < rsi_vals[-1] < 72.0
            and ctx.regime_state.kalman_slope >= 0.0
        )

        strong_buy = (
            buy_core
            and ichi["tenkan"][-1] > ichi["kijun"][-1]
            and curr_close > ichi["senkou_a"][-1]
            and curr_close > ichi["senkou_b"][-1]
        )

        sell_core = (
            fast_ma[-1] < slow_ma[-1]
            and fast_ma[-2] <= slow_ma[-2] * 1.0002
            and macd_main[-1] < macd_sig[-1]
            and st_dir[-1] < 0
            and 28.0 < rsi_vals[-1] < 60.0
            and ctx.regime_state.kalman_slope <= 0.0
        )

        strong_sell = (
            sell_core
            and ichi["tenkan"][-1] < ichi["kijun"][-1]
            and curr_close < ichi["senkou_a"][-1]
            and curr_close < ichi["senkou_b"][-1]
