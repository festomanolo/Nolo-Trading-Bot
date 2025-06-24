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
    """High-level strategy execution mode."""

    TREND_FOLLOWING = "TREND_FOLLOWING"
    RANGE_TRADING = "RANGE_TRADING"
    BREAKOUT = "BREAKOUT"
    VOLATILITY = "VOLATILITY"
    SMC_INSTITUTIONAL = "SMC_INSTITUTIONAL"
    ADAPTIVE = "ADAPTIVE"


class RiskModel(str, Enum):
    """Position sizing and risk allocation models."""

    FIXED = "FIXED"
    KELLY = "KELLY"
    ADAPTIVE_KELLY = "ADAPTIVE_KELLY"
    BAYESIAN_KELLY = "BAYESIAN_KELLY"
    ANTI_MARTINGALE = "ANTI_MARTINGALE"
    VOLATILITY_PARITY = "VOLATILITY_PARITY"


class OrderSide(str, Enum):
    """Trade direction."""

    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    """Lifecycle status of an order or position."""

    PENDING = "PENDING"
