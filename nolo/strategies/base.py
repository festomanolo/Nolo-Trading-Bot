"""Abstract base class and shared evaluation context for all alpha strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from nolo.config import BotConfig
from nolo.microstructure.orderflow import OrderFlowSnapshot
from nolo.microstructure.smc import SMCSnapshot
from nolo.types import Bar, OrderSide, RegimeState, Signal


@dataclass
class StrategyContext:
    """Rich pre-computed market context passed to every strategy on each bar/tick."""

    symbol: str
    bars: Sequence[Bar]
    htf_bars: Optional[Sequence[Bar]]
    regime_state: RegimeState
    smc_snapshot: SMCSnapshot
    orderflow: OrderFlowSnapshot
    currency_divergence: float
    config: BotConfig


class BaseStrategy(ABC):
    """Base interface for specialized regime-aware trading strategies."""

