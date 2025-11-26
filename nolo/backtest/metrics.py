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
