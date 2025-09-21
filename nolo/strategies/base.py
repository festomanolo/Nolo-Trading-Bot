"""Abstract base class and shared evaluation context for all alpha strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from nolo.config import BotConfig
from nolo.microstructure.orderflow import OrderFlowSnapshot
from nolo.microstructure.smc import SMCSnapshot
from nolo.types import Bar, OrderSide, RegimeState, Signal


@dataclass
class StrategyContext:
    """Rich pre-computed market context passed to every strategy on each bar/tick."""

    symbol: str
    bars: Sequence[Bar]
    htf_bars: Optional[Sequence[Bar]]
    regime_state: RegimeState
    smc_snapshot: SMCSnapshot
    orderflow: OrderFlowSnapshot
    currency_divergence: float
    config: BotConfig


class BaseStrategy(ABC):
    """Base interface for specialized regime-aware trading strategies."""

    name: str = "BaseStrategy"

    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()

    @abstractmethod
    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        """Inspect market context and emit a trading Signal if institutional criteria are met."""

    def compute_structural_stops(
        self,
        ctx: StrategyContext,
        side: OrderSide,
        entry_price: float,
        atr: float,
        atr_mult_override: Optional[float] = None,
    ) -> tuple[float, float]:
        """
        Calculate intelligent Stop Loss and Take Profit combining ATR and Smart Money Swing Structure.
        """
        spec = self.config.get_symbol_spec(ctx.symbol)
        mult = atr_mult_override if atr_mult_override is not None else self.config.risk.atr_sl_multiplier
        atr_dist = max(atr * mult, self.config.risk.min_sl_pips * spec.pip_size)

        if self.config.use_market_structure:
            if side == OrderSide.BUY:
                swing_low = min(ctx.smc_snapshot.last_swing_low, ctx.smc_snapshot.nearest_support)
                struct_dist = (entry_price - swing_low) * 1.12
                if struct_dist >= atr * 1.4:
                    atr_dist = (atr_dist * 0.5) + (struct_dist * 0.5)
            else:
                swing_high = max(ctx.smc_snapshot.last_swing_high, ctx.smc_snapshot.nearest_resistance)
                struct_dist = (swing_high - entry_price) * 1.12
                if struct_dist >= atr * 1.4:
                    atr_dist = (atr_dist * 0.5) + (struct_dist * 0.5)

        min_dist = self.config.risk.min_sl_pips * spec.pip_size
        max_dist = self.config.risk.max_sl_pips * spec.pip_size
        sl_dist = max(min_dist, min(max_dist, atr_dist))
        tp_dist = sl_dist * self.config.risk.risk_reward_ratio

        if side == OrderSide.BUY:
            sl = round(entry_price - sl_dist, spec.digits)
            tp = round(entry_price + tp_dist, spec.digits)
        else:
            sl = round(entry_price + sl_dist, spec.digits)
            tp = round(entry_price - tp_dist, spec.digits)
        return sl, tp

    def check_htf_alignment(self, ctx: StrategyContext, side: OrderSide) -> float:
        """
        Return +1.0 if Higher Timeframe trend confirms `side`, -1.0 if opposed, 0.5 if no HTF data.
        """
        if not self.config.use_multi_timeframe or not ctx.htf_bars or len(ctx.htf_bars) < 22:
            return 0.5
        from nolo.quant.indicators import IndicatorEngine

        htf_closes = [b.close for b in ctx.htf_bars]
        fast = IndicatorEngine.ema(htf_closes, self.config.indicators.fast_ma_period)[-1]
        slow = IndicatorEngine.ema(htf_closes, self.config.indicators.slow_ma_period)[-1]
        if side == OrderSide.BUY:
            return 1.0 if fast >= slow else -0.8
        return 1.0 if fast <= slow else -0.8
