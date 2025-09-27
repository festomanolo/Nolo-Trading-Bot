"""
Ornstein-Uhlenbeck Statistical Mean-Reversion & Bollinger/Stochastic Range Strategy.

Trades high-probability mean-reversion extremes in low-ADX / anti-persistent Hurst regimes
when Ornstein-Uhlenbeck Z-score, Bollinger Bands, RSI, and Stochastic align.
"""

from __future__ import annotations

from typing import Dict, Optional

from nolo.quant.indicators import IndicatorEngine
from nolo.quant.statistics import OrnsteinUhlenbeckEstimator
from nolo.strategies.base import BaseStrategy, StrategyContext
from nolo.types import OrderSide, Signal


class OrnsteinUhlenbeckRangeStrategy(BaseStrategy):
    """Statistical mean-reversion alpha engine for range-bound markets."""

    name = "OrnsteinUhlenbeckRange"

    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        bars = ctx.bars
        if len(bars) < 40:
            return None

        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        ind_cfg = self.config.indicators

        bb_up, bb_mid, bb_low = IndicatorEngine.bollinger_bands(
            closes, ind_cfg.bollinger_period, ind_cfg.bollinger_std
        )
        rsi_vals = IndicatorEngine.rsi(closes, ind_cfg.rsi_period)
        stoch_k, stoch_d = IndicatorEngine.stochastic(
            highs, lows, closes, ind_cfg.stoch_k, ind_cfg.stoch_d, ind_cfg.stoch_slowing
        )
        atr_vals = IndicatorEngine.atr(highs, lows, closes, ind_cfg.atr_period)
