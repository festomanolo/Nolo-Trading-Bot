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
        return self._beta_alpha / max(1e-9, self._beta_alpha + self._beta_beta)

    def update_stats(self, is_win: bool) -> None:
        self.total_trades += 1
        if is_win:
            self.winning_trades += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self._beta_alpha = self._beta_alpha * 0.98 + 1.0
            self._beta_beta = self._beta_beta * 0.98
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self._beta_alpha = self._beta_alpha * 0.98
            self._beta_beta = self._beta_beta * 0.98 + 1.0

    def compute_effective_risk_pct(
        self,
        base_risk_pct: Optional[float] = None,
        signal_win_prob: float = 0.60,
        risk_multiplier: float = 1.0,
        equity_throttle: float = 1.0,
        atr_ratio: float = 1.0,
    ) -> float:
        """Calculate effective risk % of account balance after model and streak adjustments."""
        rcfg = self.config.risk
        base = base_risk_pct if base_risk_pct is not None else rcfg.max_risk_pct
        rr = max(0.5, rcfg.risk_reward_ratio)
        model = rcfg.risk_model

        if model == RiskModel.FIXED:
            eff_pct = base

        elif model == RiskModel.KELLY:
            w = self.historical_win_rate
            kelly = max(0.002, (w - (1.0 - w) / rr) * rcfg.kelly_fraction)
            eff_pct = min(base * 1.5, kelly * 100.0 * 0.15)

        elif model == RiskModel.ADAPTIVE_KELLY:
            w = self.historical_win_rate
            streak_factor = 1.0
            if self.consecutive_losses >= 2:
                streak_factor = 0.55
            elif self.consecutive_wins >= 2:
                streak_factor = 1.20
            kelly = max(0.002, (w - (1.0 - w) / rr) * rcfg.kelly_fraction * streak_factor)
            eff_pct = min(base * 1.6, kelly * 100.0 * 0.15)

        elif model == RiskModel.BAYESIAN_KELLY:
            # Blend Bayesian posterior win rate with real-time Neural Scorer win probability
            blended_w = 0.45 * self.bayesian_win_rate + 0.55 * max(0.40, min(0.85, signal_win_prob))
            streak_factor = 1.0
            if self.consecutive_losses >= 2:
                streak_factor = max(0.45, 0.80 ** self.consecutive_losses)
            elif self.consecutive_wins >= 2:
                streak_factor = min(1.30, 1.0 + 0.08 * self.consecutive_wins)
            kelly_edge = max(0.002, (blended_w - (1.0 - blended_w) / rr) * rcfg.kelly_fraction)
            eff_pct = base * (0.65 + kelly_edge * 4.0) * streak_factor

        elif model == RiskModel.ANTI_MARTINGALE:
            if self.consecutive_losses > 0:
                eff_pct = base * 0.75
            else:
                eff_pct = base * min(1.6, 1.0 + 0.18 * self.consecutive_wins)

        elif model == RiskModel.VOLATILITY_PARITY:
            vol_scale = 1.0 / max(0.5, min(2.0, atr_ratio))
            eff_pct = base * vol_scale

        else:
            eff_pct = base

        eff_pct *= max(0.3, min(1.8, risk_multiplier)) * max(0.25, min(1.0, equity_throttle))
        return max(rcfg.min_risk_pct, min(rcfg.max_risk_pct * 1.8, eff_pct))

