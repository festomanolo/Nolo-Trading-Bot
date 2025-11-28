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

        win_rate = (len(wins) / total * 100.0) if total > 0 else 0.0
        if gross_loss > 1e-6:
            pf = gross_profit / gross_loss
        elif gross_profit > 0:
            pf = 10.0
        else:
            pf = 0.0

        expected_payoff = net_profit / total if total > 0 else 0.0
        avg_r = sum(t.r_multiple for t in trades) / total if total > 0 else 0.0

        # Max relative drawdown
        hwm = initial_balance
        max_dd_pct = 0.0
        series = list(equity_curve) if equity_curve else [initial_balance, final_balance]
        for eq in series:
            if eq > hwm:
                hwm = eq
            if hwm > 0:
                dd = ((hwm - eq) / hwm) * 100.0
                if dd > max_dd_pct:
                    max_dd_pct = dd

        # Trade return Sharpe & Sortino
        if total >= 2:
            r_vals = [t.r_multiple for t in trades]
            mean_r = sum(r_vals) / total
            var_r = sum((r - mean_r) ** 2 for r in r_vals) / (total - 1)
            std_r = math.sqrt(max(1e-12, var_r))
            sharpe = (mean_r / std_r) * math.sqrt(min(252, max(12, total)))

            downside_sq = [min(0.0, r) ** 2 for r in r_vals]
