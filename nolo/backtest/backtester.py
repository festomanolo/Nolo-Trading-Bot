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
        if not bars:
            empty_report = PerformanceAnalytics.analyze(self.initial_balance, [], [self.initial_balance])
            return BacktestResult("UNKNOWN", empty_report, [], [self.initial_balance])

        symbol = bars[0].symbol
        engine = RealTimeTradingEngine(initial_balance=self.initial_balance, config=self.config)
        n = len(bars)
        start_idx = min(max(35, warmup_bars), n)

        for i in range(start_idx, n):
            window = bars[max(0, i - 100) : i + 1]
            htf_bars = RealisticForexDataGenerator.aggregate_to_higher_timeframe(
                bars[: i + 1], ratio=htf_ratio, htf_name=self.config.higher_timeframe
            )
            engine.on_bar(symbol, window, htf_bars)

        # Close any remaining open positions at end of test
        last_bar = bars[-1]
        for ticket in list(engine.broker.open_positions.keys()):
            rec = engine.broker.close_position(
                ticket, last_bar.close, last_bar.timestamp, "END_OF_BACKTEST"
            )
            if rec:
                engine._handle_closed_trade(rec)

        eq_series = [eq for _, eq in engine.equity_curve] or [self.initial_balance, engine.broker.balance]
        report = PerformanceAnalytics.analyze(
            self.initial_balance, engine.broker.closed_trades, eq_series
        )
        return BacktestResult(
            symbol=symbol,
            report=report,
            trades=list(engine.broker.closed_trades),
            equity_curve=eq_series,
        )
