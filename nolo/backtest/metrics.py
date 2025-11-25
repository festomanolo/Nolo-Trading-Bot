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
