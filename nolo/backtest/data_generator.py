"""
Regime-Switching Stochastic Forex Market Data Generator & Historical CSV Loader.

Generates realistic multi-regime OHLCV bars exhibiting:
- Persistent trending phases (positive drift + low entropy)
- Mean-reverting Ornstein-Uhlenbeck consolidation ranges
- Institutional liquidity sweeps and volatility breakouts
- Intraday London/NY volume & spread seasonality
"""

from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Sequence

from nolo.types import Bar


class RealisticForexDataGenerator:
    """Produces deterministic or seeded realistic multi-regime Forex candlestick series."""

    @staticmethod
    def generate_bars(
        symbol: str = "EURUSD",
        timeframe: str = "M5",
        num_bars: int = 500,
        start_price: float = 1.0850,
        seed: int = 2025,
    ) -> List[Bar]:
