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
