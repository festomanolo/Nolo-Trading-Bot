"""
Institutional Performance Analytics & Strategy Tester Fitness Calculator.

Computes:
- Net Profit, Return on Investment (ROI %), Profit Factor, Expected Payoff
- Win Rate, Average Win / Average Loss, Expectancy in R-multiples
- Maximum Relative Equity Drawdown & Ulcer Index
- Annualized Sharpe Ratio, Sortino Ratio, and Calmar Ratio
- MetaTrader 5 `OnTester()` custom optimization fitness score
- Regime & Strategy Attribution breakdown
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from nolo.types import TradeRecord


@dataclass
class PerformanceReport:
    """Comprehensive institutional backtest and live performance summary."""

    initial_balance: float
    final_balance: float
    net_profit: float
    roi_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    profit_factor: float
    expected_payoff: float
    avg_r_multiple: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    on_tester_score: float
    regime_breakdown: Dict[str, int] = field(default_factory=dict)
    strategy_breakdown: Dict[str, int] = field(default_factory=dict)


class PerformanceAnalytics:
    """Computes institutional metrics from trade records and equity curves."""

    @staticmethod
    def analyze(
        initial_balance: float,
        trades: Sequence[TradeRecord],
        equity_curve: Sequence[float],
    ) -> PerformanceReport:
        total = len(trades)
        wins = [t for t in trades if t.net_pnl > 0]
        losses = [t for t in trades if t.net_pnl <= 0]

        gross_profit = sum(t.net_pnl for t in wins)
        gross_loss = abs(sum(t.net_pnl for t in losses))
        net_profit = gross_profit - gross_loss
        final_balance = initial_balance + net_profit
        roi_pct = (net_profit / max(1.0, initial_balance)) * 100.0

