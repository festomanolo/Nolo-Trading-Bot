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
