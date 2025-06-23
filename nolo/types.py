"""Core domain types, enumerations, and immutable/mutable data structures for Nolo Bot."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class RegimeType(str, Enum):
    """Detected market regime classifications."""

    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"
    BREAKOUT_UP = "BREAKOUT_UP"
    BREAKOUT_DOWN = "BREAKOUT_DOWN"
    VOLATILITY = "VOLATILITY"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"
    MIXED = "MIXED"


class StrategyMode(str, Enum):
