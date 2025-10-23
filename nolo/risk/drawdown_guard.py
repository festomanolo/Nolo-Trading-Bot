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
        self.trades_today += 1

    def record_trade_closed(self, new_balance: float) -> None:
        self.equity_history.append(new_balance)
        if len(self.equity_history) > 200:
            self.equity_history = self.equity_history[-200:]
        if new_balance > self.high_water_mark:
            self.high_water_mark = new_balance

    def daily_drawdown_pct(self, current_equity: float) -> float:
        if self.day_start_balance <= 0:
            return 0.0
        drop = self.day_start_balance - current_equity
        return max(0.0, (drop / self.day_start_balance) * 100.0)

    def total_drawdown_pct(self, current_equity: float) -> float:
        if self.high_water_mark <= 0:
            return 0.0
        drop = self.high_water_mark - current_equity
        return max(0.0, (drop / self.high_water_mark) * 100.0)

    def can_open_trade(
        self,
        current_time: datetime,
        balance: float,
        equity: float,
        bars_since_last_trade: int,
    ) -> tuple[bool, Optional[str]]:
        """Verify all Prop-Firm and risk circuit breakers before allowing trade entry."""
        self.on_new_bar_or_tick(current_time, balance, equity)
        rcfg = self.config.risk

        daily_dd = self.daily_drawdown_pct(equity)
        if daily_dd >= rcfg.max_daily_drawdown_pct:
            return False, f"Daily drawdown limit reached ({daily_dd:.2f}% >= {rcfg.max_daily_drawdown_pct:.2f}%)"

        total_dd = self.total_drawdown_pct(equity)
        if total_dd >= rcfg.max_total_drawdown_pct:
            return False, f"Max trailing drawdown reached ({total_dd:.2f}% >= {rcfg.max_total_drawdown_pct:.2f}%)"

        if self.trades_today >= rcfg.max_daily_trades:
            return False, f"Max daily trades reached ({self.trades_today}/{rcfg.max_daily_trades})"

        if bars_since_last_trade < rcfg.min_bars_between_trades:
            return False, f"Cooldown active ({bars_since_last_trade} < {rcfg.min_bars_between_trades} bars)"

        if current_time.hour in self.config.avoid_rollover_hours:
            return False, f"Rollover spread protection active (hour={current_time.hour}:00)"

        return True, None

    def equity_curve_throttle(self, current_equity: float) -> float:
        """
        Return 1.0 when equity is above its moving average, or 0.60 when below
        to automatically dampen drawdowns during losing streaks.
        """
        if not self.config.risk.use_equity_curve_filter:
            return 1.0
        w = self.config.risk.equity_ma_period
