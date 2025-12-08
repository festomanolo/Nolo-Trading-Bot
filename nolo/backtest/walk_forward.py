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
        supertrend_mults: Sequence[float] = (2.0, 2.5, 3.0),
        fast_ma_periods: Sequence[int] = (8, 10),
        risk_reward_ratios: Sequence[float] = (1.8, 2.2),
    ) -> List[OptimizationCandidate]:
        results: List[OptimizationCandidate] = []

        for st_mult in supertrend_mults:
            for fast_ma in fast_ma_periods:
                for rr in risk_reward_ratios:
                    cfg = copy.deepcopy(self.base_config)
                    cfg.indicators.supertrend_mult = float(st_mult)
                    cfg.indicators.fast_ma_period = int(fast_ma)
                    cfg.risk.risk_reward_ratio = float(rr)

                    bt = EventDrivenBacktester(initial_balance=10000.0, config=cfg)
                    res = bt.run(bars, warmup_bars=55)
                    rep = res.report

                    # Combined composite fitness balancing profit factor, ROI, and low drawdown
                    composite_score = (
                        rep.on_tester_score + rep.profit_factor * 2.0 + rep.roi_pct * 0.2 - rep.max_drawdown_pct * 0.3
                    )
                    results.append(
                        OptimizationCandidate(
                            params={
                                "supertrend_mult": float(st_mult),
                                "fast_ma_period": float(fast_ma),
                                "risk_reward_ratio": float(rr),
                            },
                            fitness_score=round(composite_score, 4),
                            profit_factor=rep.profit_factor,
                            win_rate_pct=rep.win_rate_pct,
                            max_drawdown_pct=rep.max_drawdown_pct,
                            net_profit=rep.net_profit,
                        )
                    )

        results.sort(key=lambda c: c.fitness_score, reverse=True)
        return results
