"""
Institutional Position Sizing Engine.

Implements:
- FIXED: Fixed fractional risk percentage per trade
- KELLY: Classic Kelly Criterion f* = (p - (1 - p) / b) * kelly_fraction
- ADAPTIVE_KELLY: Streak-adjusted Kelly Criterion
- BAYESIAN_KELLY: Beta-Bernoulli posterior win-rate blended with Neural Scorer probability
- ANTI_MARTINGALE: Geometric win-streak expansion with immediate loss-streak contraction
- VOLATILITY_PARITY: Inverse ATR volatility risk parity
"""

from __future__ import annotations

import math
from typing import Optional

from nolo.config import BotConfig, SymbolSpec
from nolo.types import RiskModel


class PositionSizer:
    """Computes normalized lot size and effective risk percentage for trade signals."""

    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()
        self.total_trades: int = 0
        self.winning_trades: int = 0
        self.consecutive_wins: int = 0
        self.consecutive_losses: int = 0
        self._beta_alpha: float = 6.0  # Prior equivalent to 6 wins / 4 losses (60% prior)
        self._beta_beta: float = 4.0

    @property
    def historical_win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.55
        return self.winning_trades / self.total_trades

    @property
    def bayesian_win_rate(self) -> float:
