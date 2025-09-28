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
        ou_state = OrnsteinUhlenbeckEstimator.fit(closes, window=40)

        curr_close = closes[-1]
        curr_atr = max(1e-9, atr_vals[-1])

        # Buy extreme discount / lower band / negative OU Z-score
        buy_signal = (
            (curr_close <= bb_low[-1] * 1.0005 or ou_state.z_score <= -1.65)
            and rsi_vals[-1] < 38.0
            and stoch_k[-1] < 28.0
            and stoch_k[-1] >= stoch_d[-1] * 0.95
        )

        # Sell extreme premium / upper band / positive OU Z-score
        sell_signal = (
            (curr_close >= bb_up[-1] * 0.9995 or ou_state.z_score >= 1.65)
            and rsi_vals[-1] > 62.0
            and stoch_k[-1] > 72.0
            and stoch_k[-1] <= stoch_d[-1] * 1.05
        )

        if not buy_signal and not sell_signal:
            return None

        side = OrderSide.BUY if buy_signal else OrderSide.SELL
        sl, tp = self.compute_structural_stops(ctx, side, curr_close, curr_atr, atr_mult_override=1.7)

        # Target equilibrium mean if closer/more realistic than default RR
        if side == OrderSide.BUY and bb_mid[-1] > curr_close + abs(curr_close - sl) * 1.3:
            tp = round(bb_mid[-1], self.config.get_symbol_spec(ctx.symbol).digits)
        elif side == OrderSide.SELL and bb_mid[-1] < curr_close - abs(curr_close - sl) * 1.3:
            tp = round(bb_mid[-1], self.config.get_symbol_spec(ctx.symbol).digits)
