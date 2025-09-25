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
        )

        if not buy_core and not sell_core:
            return None

        side = OrderSide.BUY if buy_core else OrderSide.SELL
        is_strong = strong_buy if side == OrderSide.BUY else strong_sell
        htf_score = self.check_htf_alignment(ctx, side)
        if htf_score < 0.0:
            return None

        sl, tp = self.compute_structural_stops(ctx, side, curr_close, curr_atr)
        dir_sign = 1.0 if side == OrderSide.BUY else -1.0

        reasons: List[str] = [
            f"EMA({ind_cfg.fast_ma_period})>{'above' if side == OrderSide.BUY else 'below'} EMA({ind_cfg.slow_ma_period})",
            f"SuperTrend direction={'BULL' if side == OrderSide.BUY else 'BEAR'}",
            f"Kalman slope={ctx.regime_state.kalman_slope:+.3f}",
        ]
        if is_strong:
            reasons.append("Ichimoku Kumo Cloud & Tenkan/Kijun full alignment")

        features: Dict[str, float] = {
            "trend_alignment": 1.0 if is_strong else 0.72,
            "kalman_velocity": min(1.0, max(-1.0, dir_sign * ctx.regime_state.kalman_slope)),
            "hurst_persistence": (ctx.regime_state.hurst_exponent - 0.5) * 2.0,
            "efficiency_ratio": ctx.regime_state.efficiency_ratio,
            "adx_strength": min(1.0, ctx.regime_state.adx / 50.0),
            "rsi_confluence": 1.0 - abs(rsi_vals[-1] - 55.0 * (1 if side == OrderSide.BUY else 0.8)) / 50.0,
            "macd_impulse": min(1.0, max(-1.0, dir_sign * macd_hist[-1] / curr_atr * 5.0)),
            "smc_zone_confluence": 0.8 if (
                (side == OrderSide.BUY and (ctx.smc_snapshot.in_bullish_ob or ctx.smc_snapshot.in_bullish_fvg))
                or (side == OrderSide.SELL and (ctx.smc_snapshot.in_bearish_ob or ctx.smc_snapshot.in_bearish_fvg))
            ) else 0.35,
            "orderflow_pressure": dir_sign * (ctx.orderflow.buy_pressure_ratio - 0.5) * 2.0,
            "currency_divergence": min(1.0, max(-1.0, dir_sign * ctx.currency_divergence / 50.0)),
            "htf_confirmation": htf_score,
            "volatility_quality": 0.85 if 0.75 <= ctx.regime_state.atr_ratio <= 1.8 else 0.45,
        }

        risk_mult = self.config.risk.adaptive_risk_multiplier if is_strong else 1.0
        return Signal(
            symbol=ctx.symbol,
            side=side,
            entry_price=curr_close,
            stop_loss=sl,
            take_profit=tp,
            confidence=0.82 if is_strong else 0.68,
