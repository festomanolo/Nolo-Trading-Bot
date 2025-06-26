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
    OPEN = "OPEN"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class SMCZoneType(str, Enum):
    """Smart Money Concepts structural zone types."""

    BULLISH_OB = "BULLISH_OB"
    BEARISH_OB = "BEARISH_OB"
    BULLISH_FVG = "BULLISH_FVG"
    BEARISH_FVG = "BEARISH_FVG"
    BUY_SIDE_LIQUIDITY = "BUY_SIDE_LIQUIDITY"
    SELL_SIDE_LIQUIDITY = "SELL_SIDE_LIQUIDITY"


class MarketStructureBias(str, Enum):
    """Institutional market structure state."""

    BULLISH_BOS = "BULLISH_BOS"
    BEARISH_BOS = "BEARISH_BOS"
    BULLISH_CHOCH = "BULLISH_CHOCH"
    BEARISH_CHOCH = "BEARISH_CHOCH"
    NEUTRAL = "NEUTRAL"


@dataclass(frozen=True)
class Tick:
    """Real-time L1 forex quote tick."""

    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    volume: float = 1.0

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) * 0.5

    @property
    def spread(self) -> float:
        return max(0.0, self.ask - self.bid)

    def spread_points(self, point: float = 0.00001) -> float:
        return self.spread / point if point > 0 else 0.0


@dataclass(frozen=True)
class Bar:
    """OHLCV candlestick bar for a given symbol and timeframe."""

    symbol: str
    timeframe: str
    timestamp: datetime
