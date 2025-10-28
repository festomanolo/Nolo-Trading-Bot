"""
Smart Exit & Open Trade Lifecycle Manager.

Implements:
1. Break-Even + Commission Buffer Stop Modification
2. Multi-Stage Partial Take-Profit (TP1 at 1.0R, TP2 at 1.8R)
3. Volatility-Adaptive ATR Trailing Stop (tightens smoothly as profit grows)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from nolo.config import BotConfig
from nolo.types import OrderSide, Position


@dataclass
class TradeAction:
    """Instruction produced by SmartTradeManager for an open position."""

    ticket: int
    action_type: str  # "MODIFY_SL", "PARTIAL_CLOSE", "FULL_CLOSE"
    new_sl: Optional[float] = None
    close_lots: float = 0.0
    reason: str = ""


class SmartTradeManager:
    """Evaluates open positions on every tick/bar for break-even, partial TP, and adaptive trailing stops."""

    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()

    def manage_position(
        self,
        pos: Position,
        bid: float,
        ask: float,
        current_atr: float,
        reference_atr: float,
    ) -> List[TradeAction]:
        """Inspect a single open position and return any required modification/close actions."""
        actions: List[TradeAction] = []
        spec = self.config.get_symbol_spec(pos.symbol)
        rcfg = self.config.risk

        mark_price = bid if pos.side == OrderSide.BUY else ask
