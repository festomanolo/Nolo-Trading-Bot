"""
Contextual Bandit Meta-Strategy Allocator (Discounted UCB1 + Bayesian Beta-Bernoulli).

Tracks strategy performance conditioned on each market regime and dynamically
scales capital & confidence weights toward the best-performing alpha strategies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

from nolo.types import RegimeType


@dataclass
class ArmStats:
    """Discounted reward statistics for a (regime, strategy) arm."""

    alpha: float = 2.0  # Beta prior wins
    beta: float = 2.0   # Beta prior losses
    pulls: float = 1.0
    cum_r: float = 0.5

    @property
    def expected_win_rate(self) -> float:
        return self.alpha / max(1e-9, self.alpha + self.beta)

    @property
    def mean_r(self) -> float:
        return self.cum_r / max(1.0, self.pulls)


class RegimeContextualBandit:
    """
    Contextual Multi-Armed Bandit that learns optimal strategy weights per Market Regime.
    Uses discounted statistics so non-stationary market shifts are adapted to quickly.
    """

    def __init__(
        self,
