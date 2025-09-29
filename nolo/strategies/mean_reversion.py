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

        dir_sign = 1.0 if side == OrderSide.BUY else -1.0
        features: Dict[str, float] = {
            "trend_alignment": 0.45,
            "kalman_velocity": 0.30,
            "hurst_persistence": (0.55 - ctx.regime_state.hurst_exponent) * 2.0,
            "efficiency_ratio": 1.0 - ctx.regime_state.efficiency_ratio,
            "adx_strength": max(0.0, 1.0 - ctx.regime_state.adx / 40.0),
            "rsi_confluence": min(1.0, abs(50.0 - rsi_vals[-1]) / 30.0),
            "macd_impulse": 0.35,
            "smc_zone_confluence": 0.85 if (
                (side == OrderSide.BUY and (ctx.smc_snapshot.bullish_liquidity_sweep or ctx.smc_snapshot.dealing_range_position < 0.25))
                or (side == OrderSide.SELL and (ctx.smc_snapshot.bearish_liquidity_sweep or ctx.smc_snapshot.dealing_range_position > 0.75))
            ) else 0.45,
            "orderflow_pressure": dir_sign * (ctx.orderflow.buy_pressure_ratio - 0.5) * 2.0,
            "currency_divergence": min(1.0, max(-1.0, dir_sign * ctx.currency_divergence / 50.0)),
            "htf_confirmation": max(0.2, self.check_htf_alignment(ctx, side)),
            "volatility_quality": 0.85 if ou_state.is_mean_reverting else 0.55,
        }

        return Signal(
            symbol=ctx.symbol,
            side=side,
            entry_price=curr_close,
