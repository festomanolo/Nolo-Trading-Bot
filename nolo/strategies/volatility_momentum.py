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
