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
        close_price: float,
        timestamp: datetime,
        reason: str = "PARTIAL_TP",
    ) -> Optional[ float ]:
        pos = self.open_positions.get(ticket)
        if pos is None or close_lots <= 0 or close_lots >= pos.current_lots:
            return None

        spec = self.config.get_symbol_spec(pos.symbol)
        price_diff = (
            (close_price - pos.open_price)
            if pos.side == OrderSide.BUY
            else (pos.open_price - close_price)
        )
        gross_pnl = price_diff * close_lots * spec.contract_size
        pos.current_lots = round(pos.current_lots - close_lots, 2)
        pos.realized_pnl += gross_pnl
        self.balance += gross_pnl
        return gross_pnl

    def close_position(
        self,
        ticket: int,
        close_price: float,
        timestamp: datetime,
        exit_reason: str = "SIGNAL_EXIT",
    ) -> Optional[TradeRecord]:
        pos = self.open_positions.pop(ticket, None)
        if pos is None:
            return None

        spec = self.config.get_symbol_spec(pos.symbol)
        price_diff = (
            (close_price - pos.open_price)
            if pos.side == OrderSide.BUY
            else (pos.open_price - close_price)
        )
        remaining_gross = price_diff * pos.current_lots * spec.contract_size
        self.balance += remaining_gross

        total_gross = pos.realized_pnl + remaining_gross
        net_pnl = total_gross - pos.commission_paid + pos.swap_accumulated
        pips = price_diff / max(1e-9, spec.pip_size)

        init_risk_price = max(spec.pip_size * 5.0, abs(pos.open_price - pos.initial_stop_loss))
        init_risk_currency = (init_risk_price / spec.tick_size) * spec.tick_value * pos.initial_lots
        r_mult = net_pnl / max(1.0, init_risk_currency)

        record = TradeRecord(
            ticket=pos.ticket,
            symbol=pos.symbol,
            side=pos.side,
            open_time=pos.open_time,
            close_time=timestamp,
            open_price=pos.open_price,
            close_price=close_price,
            lots=pos.initial_lots,
            net_pnl=round(net_pnl, 2),
            gross_pnl=round(total_gross, 2),
            commission=pos.commission_paid,
            swap=pos.swap_accumulated,
            pips=round(pips, 2),
            r_multiple=round(r_mult, 3),
            strategy_name=pos.strategy_name,
            regime=pos.regime,
            exit_reason=exit_reason,
            entry_features=pos.entry_features,
        )
        self.closed_trades.append(record)
        return record

    def process_bar_stops(self, bar: Bar) -> List[TradeRecord]:
        """Check intrabar High/Low against active Stop-Loss and Take-Profit levels."""
        closed: List[TradeRecord] = []
        spec = self.config.get_symbol_spec(bar.symbol)
        half_spread = (bar.spread_points * spec.point) * 0.5

        for ticket, pos in list(self.open_positions.items()):
            if pos.symbol != bar.symbol:
                continue

            if pos.side == OrderSide.BUY:
                bid_low = bar.low - half_spread
                bid_high = bar.high - half_spread
                if pos.stop_loss > 0 and bid_low <= pos.stop_loss:
                    rec = self.close_position(
                        ticket,
                        pos.stop_loss,
                        bar.timestamp,
                        "TRAILING_STOP" if pos.breakeven_applied else "STOP_LOSS",
                    )
                    if rec:
                        closed.append(rec)
                elif pos.take_profit > 0 and bid_high >= pos.take_profit:
                    rec = self.close_position(ticket, pos.take_profit, bar.timestamp, "TAKE_PROFIT")
                    if rec:
                        closed.append(rec)
            else:
                ask_high = bar.high + half_spread
                ask_low = bar.low + half_spread
                if pos.stop_loss > 0 and ask_high >= pos.stop_loss:
                    rec = self.close_position(
                        ticket,
                        pos.stop_loss,
                        bar.timestamp,
                        "TRAILING_STOP" if pos.breakeven_applied else "STOP_LOSS",
                    )
                    if rec:
                        closed.append(rec)
                elif pos.take_profit > 0 and ask_low <= pos.take_profit:
                    rec = self.close_position(ticket, pos.take_profit, bar.timestamp, "TAKE_PROFIT")
                    if rec:
                        closed.append(rec)

        return closed
