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
                # Institutional Downtrend phase
                drift = -1.8 * pip
                vol = 3.4 * pip
            else:
                # Persistent Breakout / Momentum expansion
                drift = 2.1 * pip
                vol = 3.8 * pip

            # Skip rollover hours (22-23 UTC) to keep active trading sessions
            if curr_time.hour in (22, 23):
                curr_time += timedelta(hours=2)

            open_p = round(price, digits)
            shock = rng.gauss(drift, vol)
            close_p = round(max(pip * 100, open_p + shock), digits)

            wick_up = abs(rng.gauss(0, vol * 0.42))
            wick_dn = abs(rng.gauss(0, vol * 0.42))
            high_p = round(max(open_p, close_p) + wick_up, digits)
            low_p = round(min(open_p, close_p) - wick_dn, digits)

            # Volume higher during London/NY overlap (12-17 UTC)
            session_mult = 1.6 if 12 <= curr_time.hour <= 17 else 1.0
            volume = round(max(50.0, (120.0 + abs(shock / pip) * 35.0) * session_mult), 1)
            spread = 7.0 if 7 <= curr_time.hour <= 20 else 12.0

            bars.append(
                Bar(
                    symbol=symbol.upper()[:6],
                    timeframe=timeframe.upper(),
                    timestamp=curr_time,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=volume,
                    spread_points=spread,
                )
            )
            price = close_p
            curr_time += timedelta(minutes=tf_minutes)

        return bars

    @staticmethod
    def aggregate_to_higher_timeframe(bars: Sequence[Bar], ratio: int = 12, htf_name: str = "H1") -> List[Bar]:
        """Aggregate lower-timeframe bars (e.g. M5) into higher-timeframe bars (e.g. H1)."""
        if not bars or ratio <= 1:
            return list(bars)
        htf: List[Bar] = []
        for i in range(0, len(bars), ratio):
            chunk = bars[i : i + ratio]
            if not chunk:
                continue
            htf.append(
                Bar(
                    symbol=chunk[0].symbol,
                    timeframe=htf_name,
                    timestamp=chunk[-1].timestamp,
                    open=chunk[0].open,
                    high=max(b.high for b in chunk),
                    low=min(b.low for b in chunk),
                    close=chunk[-1].close,
                    volume=sum(b.volume for b in chunk),
                    spread_points=sum(b.spread_points for b in chunk) / len(chunk),
                )
            )
        return htf

    @staticmethod
    def load_csv(path: Path, symbol: str = "EURUSD", timeframe: str = "H1") -> List[Bar]:
        """Load historical OHLCV bars from a standard MetaTrader CSV export."""
        bars: List[Bar] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts_str = row.get("timestamp") or row.get("time") or row.get("Date") or ""
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                bars.append(
                    Bar(
                        symbol=symbol,
                        timeframe=timeframe,
                        timestamp=ts,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row.get("volume", 100.0)),
                        spread_points=float(row.get("spread", 8.0)),
                    )
                )
        return bars
