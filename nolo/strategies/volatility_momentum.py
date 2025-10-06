"""
TTM Volatility Squeeze & Order Flow Momentum Expansion Strategy.

Designed for explosive volatility regimes:
- Detects Bollinger-inside-Keltner Volatility Squeeze release or ATR expansion (>1.25x)
- Confirms momentum acceleration via Fast EMA slope, RSI surge, and Order Flow CVD delta
- Uses tighter dynamic stop-loss (1.5x ATR) to protect capital during high volatility
"""

from __future__ import annotations

from typing import Dict, Optional

from nolo.quant.indicators import IndicatorEngine
from nolo.strategies.base import BaseStrategy, StrategyContext
from nolo.types import OrderSide, Signal


class VolatilitySqueezeMomentumStrategy(BaseStrategy):
    """High-velocity momentum strategy for volatility expansion regimes."""

    name = "VolatilitySqueezeMomentum"

    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        bars = ctx.bars
        if len(bars) < 30:
            return None

        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        ind_cfg = self.config.indicators

        fast_ma = IndicatorEngine.ema(closes, ind_cfg.fast_ma_period)
        rsi_vals = IndicatorEngine.rsi(closes, ind_cfg.rsi_period)
        atr_vals = IndicatorEngine.atr(highs, lows, closes, ind_cfg.atr_period)
        squeeze_on, squeeze_mom = IndicatorEngine.ttm_squeeze(
            highs, lows, closes, ind_cfg.bollinger_period, ind_cfg.bollinger_std, ind_cfg.keltner_atr_mult
        )

        curr_atr = max(1e-9, atr_vals[-1])
        expanding_vol = curr_atr > atr_vals[-6] * 1.22 or (any(squeeze_on[-5:-1]) and not squeeze_on[-1])
        if not expanding_vol and self.config.use_volatility_filter:
            return None

        buy_signal = (
            fast_ma[-1] > fast_ma[-2] > fast_ma[-3]
            and rsi_vals[-1] > 52.0
            and (rsi_vals[-1] >= rsi_vals[-2] + 3.5 or squeeze_mom[-1] > squeeze_mom[-2] > 0)
            and ctx.orderflow.buy_pressure_ratio >= 0.52
