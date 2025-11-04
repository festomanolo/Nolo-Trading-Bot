"""
Realistic ECN Paper & Backtest Broker Engine.

Models:
- Bid/Ask spread execution (BUY at Ask, SELL at Bid)
- Slippage modeling proportional to order size and volatility
- ECN round-turn commission per lot
- Partial position closes, SL/TP triggers, and real-time mark-to-market equity
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from nolo.config import BotConfig
from nolo.types import Bar, OrderSide, Position, Signal, TradeRecord


class RealisticECNBroker:
    """Institutional ECN broker execution simulator for live paper trading and backtesting."""

    def __init__(self, initial_balance: float = 10000.0, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()
        self.initial_balance = float(initial_balance)
        self.balance = float(initial_balance)
        self.open_positions: Dict[int, Position] = {}
        self.closed_trades: List[TradeRecord] = []
        self._next_ticket: int = 1001

    @property
    def equity(self) -> float:
        unrealized = 0.0
        for pos in self.open_positions.values():
            spec = self.config.get_symbol_spec(pos.symbol)
            unrealized += pos.unrealized_pnl(spec.contract_size)
        return self.balance + unrealized

    def open_order(
        self,
        signal: Signal,
        lots: float,
        timestamp: datetime,
        spread_points: float = 8.0,
    ) -> Position:
        spec = self.config.get_symbol_spec(signal.symbol)
        half_spread = (spread_points * spec.point) * 0.5
        fill_price = (
            round(signal.entry_price + half_spread, spec.digits)
            if signal.side == OrderSide.BUY
            else round(signal.entry_price - half_spread, spec.digits)
        )
        commission = round(lots * spec.commission_per_lot, 2)
        self.balance -= commission

        ticket = self._next_ticket
        self._next_ticket += 1

        pos = Position(
            ticket=ticket,
            symbol=signal.symbol,
            side=signal.side,
            open_time=timestamp,
            open_price=fill_price,
            current_price=fill_price,
            initial_lots=lots,
            current_lots=lots,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            initial_stop_loss=signal.stop_loss,
            strategy_name=signal.strategy_name,
            regime=signal.regime,
            magic=self.config.magic_number,
            commission_paid=commission,
            entry_features=dict(signal.features),
        )
        self.open_positions[ticket] = pos
        return pos

    def modify_stop_loss(self, ticket: int, new_sl: float) -> bool:
        pos = self.open_positions.get(ticket)
        if pos is None:
            return False
        pos.stop_loss = new_sl
        return True

    def partial_close(
        self,
        ticket: int,
        close_lots: float,
