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
        rng = random.Random(seed)
        is_jpy = "JPY" in symbol.upper()
        pip = 0.01 if is_jpy else 0.0001
        digits = 3 if is_jpy else 5

        tf_minutes = {"M1": 1, "M5": 5, "M15": 15, "H1": 60, "H4": 240, "D1": 1440}.get(
            timeframe.upper(), 5
        )
        curr_time = datetime(2025, 1, 6, 8, 0, tzinfo=timezone.utc)
        price = start_price
        bars: List[Bar] = []

        # Cycle through realistic multi-session market regimes
        for i in range(num_bars):
            phase = (i // 160) % 4
            if phase == 0:
                # Institutional Uptrend phase
                drift = 1.9 * pip
                vol = 3.2 * pip
            elif phase == 1:
                # Mean-reverting consolidation range
                anchor = price if i % 160 == 0 else bars[-1].close
                drift = -0.30 * (price - anchor)
                vol = 2.5 * pip
            elif phase == 2:
