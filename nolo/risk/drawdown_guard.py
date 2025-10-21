"""
Prop-Firm Compliant Daily & Trailing Drawdown Guard + Equity Curve Filter.

Enforces:
1. Daily Balance & Equity Drawdown Limit (resets each trading day)
2. Maximum Overall Trailing Drawdown from High-Water Mark (FTMO / Prop-Firm protection)
3. Daily Trade Count Cap & Minimum Bars Since Last Trade
4. Equity Curve Moving Average Throttle (scales risk down by 50% when equity < SMA(equity))
5. Midnight Rollover / Illiquid Session Guard
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from nolo.config import BotConfig


class DrawdownAndPropGuard:
    """Monitors account equity, daily high-water marks, and session safety rules."""

    def __init__(self, initial_balance: float, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()
        self.initial_balance = max(1.0, float(initial_balance))
        self.high_water_mark = self.initial_balance
        self.day_start_balance = self.initial_balance
        self.current_day: Optional[date] = None
        self.trades_today: int = 0
        self.equity_history: List[float] = [self.initial_balance]

    def on_new_bar_or_tick(self, current_time: datetime, balance: float, equity: float) -> None:
        today = current_time.date()
        if self.current_day != today:
            self.current_day = today
            self.day_start_balance = max(balance, equity)
            self.trades_today = 0

        if equity > self.high_water_mark:
            self.high_water_mark = equity

    def record_trade_opened(self) -> None:
