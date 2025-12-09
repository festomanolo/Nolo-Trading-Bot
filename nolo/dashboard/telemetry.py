"""
Real-Time Institutional Telemetry & Dashboard State Exporter.

Builds structured snapshots of the trading engine, regime probabilities,
currency strength matrix, active Smart Money zones, and equity curve.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from nolo.backtest.metrics import PerformanceAnalytics
from nolo.execution.engine import RealTimeTradingEngine


class TelemetryBuilder:
    """Extracts complete real-time telemetry state from `RealTimeTradingEngine`."""

    @staticmethod
    def build_snapshot(engine: RealTimeTradingEngine) -> Dict[str, Any]:
        eq_values = [eq for _, eq in engine.equity_curve] or [engine.broker.initial_balance]
        perf = PerformanceAnalytics.analyze(
            engine.broker.initial_balance,
            engine.broker.closed_trades,
            eq_values,
        )
        regimes: Dict[str, Any] = {}
        for sym, r in engine.latest_regimes.items():
            regimes[sym] = {
