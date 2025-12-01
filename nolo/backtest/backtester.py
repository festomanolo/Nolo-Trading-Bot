"""
Event-Driven Multi-Timeframe Backtester.

Replays historical or synthesized OHLCV bar streams chronologically without look-ahead bias,
maintaining synchronized Higher Timeframe (HTF) bars and full ECN execution accounting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from nolo.backtest.data_generator import RealisticForexDataGenerator
from nolo.backtest.metrics import PerformanceAnalytics, PerformanceReport
from nolo.config import BotConfig
from nolo.execution.engine import RealTimeTradingEngine
from nolo.types import Bar, TradeRecord


@dataclass
class BacktestResult:
    """Output of a complete event-driven backtest run."""

    symbol: str
    report: PerformanceReport
    trades: List[TradeRecord]
    equity_curve: List[float]


class EventDrivenBacktester:
    """Runs chronological event-driven backtests on `RealTimeTradingEngine`."""

    def __init__(self, initial_balance: float = 10000.0, config: Optional[BotConfig] = None) -> None:
        self.initial_balance = float(initial_balance)
        self.config = config or BotConfig()

    def run(
        self,
        bars: Sequence[Bar],
        htf_ratio: int = 12,
        warmup_bars: int = 55,
    ) -> BacktestResult:
