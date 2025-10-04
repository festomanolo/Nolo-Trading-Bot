"""
Institutional Smart Money Concepts (SMC) Liquidity Sweep & Breakout Strategy.

Captures two institutional setups:
1. Volume-confirmed structural Breakout (BOS) with expanding ATR & Order Flow confirmation
2. Liquidity Sweep (Stop Hunt) reversal from an unmitigated Order Block or Fair Value Gap
"""

from __future__ import annotations

from typing import Dict, List, Optional

from nolo.quant.indicators import IndicatorEngine
from nolo.strategies.base import BaseStrategy, StrategyContext
from nolo.types import MarketStructureBias, OrderSide, Signal


class SMCLiquidityBreakoutStrategy(BaseStrategy):
    """Trades institutional breakouts (BOS) and liquidity stop-hunt sweeps."""

    name = "SMCLiquidityBreakout"

    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        bars = ctx.bars
        if len(bars) < 30:
            return None

        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        ind_cfg = self.config.indicators

        rsi_vals = IndicatorEngine.rsi(closes, ind_cfg.rsi_period)
        atr_vals = IndicatorEngine.atr(highs, lows, closes, ind_cfg.atr_period)

        curr_close = closes[-1]
        curr_atr = max(1e-9, atr_vals[-1])
        recent_high = max(highs[-21:-1])
        recent_low = min(lows[-21:-1])

        vol_surge = ctx.orderflow.volume_surge_ratio >= 1.25 or bars[-1].volume > bars[-2].volume * 1.35
        vol_confirm = ctx.regime_state.atr_ratio >= 1.05

        # Setup A: Structural Breakout (BOS) with volume surge
        bos_buy = (
            curr_close > recent_high
            and vol_surge
            and vol_confirm
            and rsi_vals[-1] > 52.0
        )
        bos_sell = (
            curr_close < recent_low
            and vol_surge
            and vol_confirm
            and rsi_vals[-1] < 48.0
        )

        # Setup B: Institutional Liquidity Sweep / Order Block Mitigation
        smc_buy = (
            ctx.smc_snapshot.bullish_liquidity_sweep
            or (
                (ctx.smc_snapshot.in_bullish_ob or ctx.smc_snapshot.in_bullish_fvg)
                and ctx.smc_snapshot.structure_bias
                in (MarketStructureBias.BULLISH_BOS, MarketStructureBias.BULLISH_CHOCH)
                and bars[-1].is_bullish
            )
        )
        smc_sell = (
            ctx.smc_snapshot.bearish_liquidity_sweep
            or (
                (ctx.smc_snapshot.in_bearish_ob or ctx.smc_snapshot.in_bearish_fvg)
                and ctx.smc_snapshot.structure_bias
                in (MarketStructureBias.BEARISH_BOS, MarketStructureBias.BEARISH_CHOCH)
                and not bars[-1].is_bullish
            )
        )

        is_buy = bos_buy or smc_buy
        is_sell = bos_sell or smc_sell
        if not is_buy and not is_sell:
            return None

        side = OrderSide.BUY if is_buy else OrderSide.SELL
        htf_score = self.check_htf_alignment(ctx, side)
        if htf_score < -0.5 and not (ctx.smc_snapshot.bullish_liquidity_sweep or ctx.smc_snapshot.bearish_liquidity_sweep):
            return None

        sl, tp = self.compute_structural_stops(ctx, side, curr_close, curr_atr, atr_mult_override=1.8)
        dir_sign = 1.0 if side == OrderSide.BUY else -1.0

        reasons: List[str] = []
        if bos_buy or bos_sell:
            reasons.append(f"20-bar Structural Breakout with volume surge ({ctx.orderflow.volume_surge_ratio:.2f}x)")
        if smc_buy or smc_sell:
            reasons.append(f"SMC Institutional Zone / Liquidity Sweep ({ctx.smc_snapshot.structure_bias.value})")

        features: Dict[str, float] = {
            "trend_alignment": 0.70,
            "kalman_velocity": min(1.0, max(-1.0, dir_sign * ctx.regime_state.kalman_slope)),
            "hurst_persistence": (ctx.regime_state.hurst_exponent - 0.48) * 2.0,
            "efficiency_ratio": ctx.regime_state.efficiency_ratio,
            "adx_strength": min(1.0, ctx.regime_state.adx / 45.0),
            "rsi_confluence": 0.75,
            "macd_impulse": 0.60,
            "smc_zone_confluence": 0.92 if (smc_buy or smc_sell) else 0.65,
            "orderflow_pressure": dir_sign * (ctx.orderflow.buy_pressure_ratio - 0.5) * 2.0,
            "currency_divergence": min(1.0, max(-1.0, dir_sign * ctx.currency_divergence / 50.0)),
            "htf_confirmation": max(0.0, htf_score),
            "volatility_quality": min(1.0, ctx.regime_state.atr_ratio / 1.5),
        }

        return Signal(
            symbol=ctx.symbol,
            side=side,
            entry_price=curr_close,
            stop_loss=sl,
            take_profit=tp,
            confidence=0.78 if (smc_buy or smc_sell) else 0.70,
            win_probability=0.64,
            strategy_name=self.name,
            regime=ctx.regime_state.regime,
            risk_multiplier=0.88 if (bos_buy or bos_sell) else 1.05,
            expected_rr=self.config.risk.risk_reward_ratio,
            features=features,
            reasons=reasons,
            timestamp=bars[-1].timestamp,
        )
