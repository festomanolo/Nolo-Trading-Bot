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
