"""
Institutional Technical & Quantitative Indicator Engine.

Provides exact, streaming-safe implementations of:
- Exponential & Simple Moving Averages (EMA, SMA, Wilder's RMA)
- Wilder's RSI & RSI Divergence detector
- MACD (Main, Signal, Histogram)
- Bollinger Bands & Keltner Channels & TTM Volatility Squeeze
- Average True Range (ATR) & Chandelier Exit
- Average Directional Index (ADX, +DI, -DI)
- SuperTrend (adaptive ATR trend-following bands)
- Ichimoku Kinko Hyo (Tenkan-sen, Kijun-sen, Senkou Span A/B)
- Stochastic Oscillator (%K, %D)
- Volume-Weighted Average Price (VWAP)
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

from nolo.types import Bar


class IndicatorEngine:
    """Pure-Python high-precision quantitative indicator calculator."""

    @staticmethod
    def sma(values: Sequence[float], period: int) -> List[float]:
        n = len(values)
        if n == 0 or period <= 1:
            return [float(x) for x in values]
        out: List[float] = []
        running_sum = 0.0
        for i, val in enumerate(values):
            v = float(val)
            running_sum += v
            if i >= period:
                running_sum -= float(values[i - period])
                out.append(running_sum / period)
            else:
                out.append(running_sum / (i + 1))
        return out

    @staticmethod
    def ema(values: Sequence[float], period: int) -> List[float]:
        n = len(values)
        if n == 0:
            return []
        if period <= 1:
            return [float(x) for x in values]
        alpha = 2.0 / (period + 1.0)
        out: List[float] = [float(values[0])]
        for i in range(1, n):
            prev = out[-1]
            out.append(alpha * float(values[i]) + (1.0 - alpha) * prev)
