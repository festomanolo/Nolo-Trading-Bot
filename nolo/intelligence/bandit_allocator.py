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
        strategy_names: Iterable[str],
        exploration_c: float = 0.65,
        discount_gamma: float = 0.97,
    ) -> None:
        self.strategy_names: List[str] = list(strategy_names)
        self.exploration_c = exploration_c
        self.discount_gamma = max(0.80, min(1.0, discount_gamma))
        self._table: Dict[str, Dict[str, ArmStats]] = {}
        for r in RegimeType:
            self._table[r.value] = {s: ArmStats() for s in self.strategy_names}

    def get_strategy_weight(self, regime: RegimeType, strategy_name: str) -> float:
        """
        Return a dynamic multiplier in [0.5, 1.6] for `strategy_name` in `regime`
        using Upper Confidence Bound (UCB1) + Bayesian win rate posterior.
        """
        regime_arms = self._table.setdefault(regime.value, {})
        arm = regime_arms.setdefault(strategy_name, ArmStats())

        total_pulls = sum(a.pulls for a in regime_arms.values())
        ucb_bonus = self.exploration_c * math.sqrt(
            math.log(max(2.0, total_pulls)) / max(1.0, arm.pulls)
        )
        base_score = 0.6 * arm.expected_win_rate + 0.4 * max(0.0, min(1.0, (arm.mean_r + 1.0) / 3.0))
        raw = base_score + 0.25 * min(1.5, ucb_bonus)
