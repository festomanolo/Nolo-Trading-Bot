"""
Monte Carlo Trade Sequence Permutation & Drawdown Stress Tester.

Evaluates tail-risk robustness by reshuffling realized trade PnLs with replacement
across N simulations to estimate 95% and 99% Value-at-Risk (VaR) and Conditional VaR (CVaR)
of maximum drawdown.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence

from nolo.types import TradeRecord


@dataclass(frozen=True)
class MonteCarloResult:
    """Tail-risk confidence intervals from Monte Carlo trade permutation simulations."""

    iterations: int
    median_net_profit: float
    p5_net_profit: float
    p95_net_profit: float
    median_max_drawdown_pct: float
    var_95_max_drawdown_pct: float
    cvar_99_max_drawdown_pct: float
    probability_of_profit_pct: float


class MonteCarloStressTester:
    """Performs bootstrap resampling and permutation stress tests on trade histories."""

    @staticmethod
    def run_simulations(
        initial_balance: float,
        trades: Sequence[TradeRecord],
        iterations: int = 500,
        seed: int = 2025,
    ) -> MonteCarloResult:
        if not trades or iterations <= 0:
            return MonteCarloResult(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        rng = random.Random(seed)
        pnls = [t.net_pnl for t in trades]
        n = len(pnls)

        net_profits: List[float] = []
        max_dds: List[float] = []
        profitable_runs = 0

        for _ in range(iterations):
            sampled = [rng.choice(pnls) for _ in range(n)]
            eq = initial_balance
            hwm = initial_balance
            max_dd = 0.0
            for p in sampled:
                eq += p
                if eq > hwm:
                    hwm = eq
                if hwm > 0:
                    dd = ((hwm - eq) / hwm) * 100.0
                    if dd > max_dd:
                        max_dd = dd
            net = eq - initial_balance
            net_profits.append(net)
            max_dds.append(max_dd)
            if net > 0:
                profitable_runs += 1

        net_profits.sort()
        max_dds.sort()

        def pct(arr: List[float], q: float) -> float:
            idx = max(0, min(len(arr) - 1, int(q * (len(arr) - 1))))
            return arr[idx]

        tail_start = max(0, int(0.95 * len(max_dds)))
        cvar_99 = sum(max_dds[tail_start:]) / max(1, len(max_dds) - tail_start)

        return MonteCarloResult(
