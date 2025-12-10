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
                "regime": r.regime.value,
                "confidence": round(r.confidence, 4),
                "hurst": round(r.hurst_exponent, 4),
                "efficiency_ratio": round(r.efficiency_ratio, 4),
                "adx": round(r.adx, 2),
                "kalman_slope": round(r.kalman_slope, 4),
                "entropy": round(r.entropy, 4),
                "structure_bias": r.structure_bias.value,
            }

        return {
            "account": {
                "initial_balance": engine.broker.initial_balance,
                "balance": round(engine.broker.balance, 2),
                "equity": round(engine.broker.equity, 2),
                "daily_drawdown_pct": round(
                    engine.drawdown_guard.daily_drawdown_pct(engine.broker.equity), 2
                ),
                "total_drawdown_pct": round(
                    engine.drawdown_guard.total_drawdown_pct(engine.broker.equity), 2
                ),
                "open_positions_count": len(engine.broker.open_positions),
            },
