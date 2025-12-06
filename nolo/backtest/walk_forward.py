"""
Walk-Forward Parameter Optimizer.

Evaluates parameter grids across In-Sample (IS) and Out-of-Sample (OOS) windows
to select robust indicator and risk hyperparameters that prevent overfitting.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Dict, List, Sequence

from nolo.backtest.backtester import EventDrivenBacktester
from nolo.config import BotConfig
from nolo.types import Bar


@dataclass
class OptimizationCandidate:
    """Result of evaluating a parameter set during Walk-Forward Optimization."""

    params: Dict[str, float]
    fitness_score: float
    profit_factor: float
    win_rate_pct: float
    max_drawdown_pct: float
    net_profit: float


class WalkForwardOptimizer:
    """Optimizes SuperTrend multiplier, Fast/Slow EMA periods, and Risk-Reward ratio."""

    def __init__(self, base_config: BotConfig | None = None) -> None:
        self.base_config = base_config or BotConfig()

    def optimize(
        self,
        bars: Sequence[Bar],
