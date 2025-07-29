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
        return out

    @staticmethod
    def rma(values: Sequence[float], period: int) -> List[float]:
        """Wilder's Smoothing Moving Average (alpha = 1 / period)."""
        n = len(values)
        if n == 0:
            return []
        if period <= 1:
            return [float(x) for x in values]
        alpha = 1.0 / period
        out: List[float] = [float(values[0])]
        for i in range(1, n):
            out.append(alpha * float(values[i]) + (1.0 - alpha) * out[-1])
        return out

    @staticmethod
    def rsi(closes: Sequence[float], period: int = 14) -> List[float]:
        n = len(closes)
        if n == 0:
            return []
        if n == 1:
            return [50.0]

        gains = [0.0]
        losses = [0.0]
        for i in range(1, n):
            diff = float(closes[i]) - float(closes[i - 1])
            gains.append(max(0.0, diff))
            losses.append(max(0.0, -diff))

        avg_gains = IndicatorEngine.rma(gains, period)
        avg_losses = IndicatorEngine.rma(losses, period)

        result: List[float] = []
        for g, l in zip(avg_gains, avg_losses):
            if l <= 1e-12 and g <= 1e-12:
                result.append(50.0)
            elif l <= 1e-12:
                result.append(100.0)
            else:
                rs = g / l
                result.append(100.0 - (100.0 / (1.0 + rs)))
        return result

    @staticmethod
    def macd(
        closes: Sequence[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Tuple[List[float], List[float], List[float]]:
        """Return (macd_main, macd_signal, macd_histogram)."""
        if not closes:
            return [], [], []
        fast_ema = IndicatorEngine.ema(closes, fast_period)
        slow_ema = IndicatorEngine.ema(closes, slow_period)
        main = [f - s for f, s in zip(fast_ema, slow_ema)]
        signal = IndicatorEngine.ema(main, signal_period)
        hist = [m - s for m, s in zip(main, signal)]
        return main, signal, hist

    @staticmethod
    def bollinger_bands(
        closes: Sequence[float],
        period: int = 20,
        std_dev: float = 2.0,
    ) -> Tuple[List[float], List[float], List[float]]:
        """Return (upper_band, middle_band, lower_band)."""
        n = len(closes)
        if n == 0:
            return [], [], []
        mid = IndicatorEngine.sma(closes, period)
        upper: List[float] = []
        lower: List[float] = []
        for i in range(n):
            start = max(0, i - period + 1)
            window = [float(closes[j]) for j in range(start, i + 1)]
            m = mid[i]
            var = sum((x - m) ** 2 for x in window) / len(window)
            sd = math.sqrt(var)
            upper.append(m + std_dev * sd)
            lower.append(m - std_dev * sd)
        return upper, mid, lower

    @staticmethod
    def atr(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        period: int = 14,
    ) -> List[float]:
        n = min(len(highs), len(lows), len(closes))
        if n == 0:
            return []
        tr: List[float] = [max(1e-9, float(highs[0]) - float(lows[0]))]
        for i in range(1, n):
            h = float(highs[i])
            l = float(lows[i])
            pc = float(closes[i - 1])
            tr.append(max(h - l, abs(h - pc), abs(l - pc)))
        return IndicatorEngine.rma(tr, period)

    @staticmethod
    def adx(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        period: int = 14,
    ) -> Tuple[List[float], List[float], List[float]]:
        """Return (adx_values, plus_di, minus_di)."""
        n = min(len(highs), len(lows), len(closes))
        if n == 0:
            return [], [], []

        plus_dm = [0.0]
        minus_dm = [0.0]
        tr = [max(1e-9, float(highs[0]) - float(lows[0]))]

        for i in range(1, n):
            up_move = float(highs[i]) - float(highs[i - 1])
            down_move = float(lows[i - 1]) - float(lows[i])
            plus_dm.append(up_move if (up_move > down_move and up_move > 0) else 0.0)
            minus_dm.append(down_move if (down_move > up_move and down_move > 0) else 0.0)
            h = float(highs[i])
            l = float(lows[i])
            pc = float(closes[i - 1])
            tr.append(max(h - l, abs(h - pc), abs(l - pc)))

