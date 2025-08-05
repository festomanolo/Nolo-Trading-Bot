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

        atr_vals = IndicatorEngine.rma(tr, period)
        sm_plus = IndicatorEngine.rma(plus_dm, period)
        sm_minus = IndicatorEngine.rma(minus_dm, period)

        plus_di: List[float] = []
        minus_di: List[float] = []
        dx: List[float] = []

        for p, m, a in zip(sm_plus, sm_minus, atr_vals):
            if a <= 1e-12:
                p_di, m_di = 0.0, 0.0
            else:
                p_di = 100.0 * (p / a)
                m_di = 100.0 * (m / a)
            plus_di.append(p_di)
            minus_di.append(m_di)
            denom = p_di + m_di
            dx.append(100.0 * abs(p_di - m_di) / denom if denom > 1e-12 else 0.0)

        adx_vals = IndicatorEngine.rma(dx, period)
        return adx_vals, plus_di, minus_di

    @staticmethod
    def supertrend(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        atr_period: int = 14,
        multiplier: float = 2.5,
    ) -> Tuple[List[float], List[int]]:
        """
        Calculate SuperTrend line and direction (+1 bullish, -1 bearish).
        Fixes standard band ratcheting so bands only tighten in the trend direction.
        """
        n = min(len(highs), len(lows), len(closes))
        if n == 0:
            return [], []

        atr_vals = IndicatorEngine.atr(highs, lows, closes, atr_period)
        st_line: List[float] = [0.0] * n
        st_dir: List[int] = [1] * n
        final_upper: List[float] = [0.0] * n
        final_lower: List[float] = [0.0] * n

        for i in range(n):
            hl2 = (float(highs[i]) + float(lows[i])) * 0.5
            basic_upper = hl2 + multiplier * atr_vals[i]
            basic_lower = hl2 - multiplier * atr_vals[i]

            if i == 0:
                final_upper[i] = basic_upper
                final_lower[i] = basic_lower
                st_dir[i] = 1
                st_line[i] = final_lower[i]
                continue

            prev_close = float(closes[i - 1])
            if basic_upper < final_upper[i - 1] or prev_close > final_upper[i - 1]:
                final_upper[i] = basic_upper
            else:
                final_upper[i] = final_upper[i - 1]

            if basic_lower > final_lower[i - 1] or prev_close < final_lower[i - 1]:
                final_lower[i] = basic_lower
            else:
                final_lower[i] = final_lower[i - 1]

            curr_close = float(closes[i])
            prev_dir = st_dir[i - 1]
            if prev_dir == -1 and curr_close > final_upper[i - 1]:
                st_dir[i] = 1
            elif prev_dir == 1 and curr_close < final_lower[i - 1]:
                st_dir[i] = -1
            else:
                st_dir[i] = prev_dir

            st_line[i] = final_lower[i] if st_dir[i] == 1 else final_upper[i]

        return st_line, st_dir

    @staticmethod
    def ichimoku(
        highs: Sequence[float],
        lows: Sequence[float],
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_b_period: int = 52,
    ) -> Dict[str, List[float]]:
        """Compute Tenkan-sen, Kijun-sen, Senkou Span A, and Senkou Span B."""
        n = min(len(highs), len(lows))
        if n == 0:
            return {"tenkan": [], "kijun": [], "senkou_a": [], "senkou_b": []}

        def midpoint_series(period: int) -> List[float]:
            out: List[float] = []
            for i in range(n):
                start = max(0, i - period + 1)
                hh = max(float(highs[j]) for j in range(start, i + 1))
                ll = min(float(lows[j]) for j in range(start, i + 1))
                out.append((hh + ll) * 0.5)
            return out

        tenkan = midpoint_series(tenkan_period)
        kijun = midpoint_series(kijun_period)
        senkou_a = [(t + k) * 0.5 for t, k in zip(tenkan, kijun)]
        senkou_b = midpoint_series(senkou_b_period)
        return {
            "tenkan": tenkan,
            "kijun": kijun,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b,
        }

    @staticmethod
    def stochastic(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        k_period: int = 5,
        d_period: int = 3,
        slowing: int = 3,
    ) -> Tuple[List[float], List[float]]:
        """Return (stoch_main_%K, stoch_signal_%D)."""
        n = min(len(highs), len(lows), len(closes))
        if n == 0:
            return [], []

        raw_num: List[float] = []
        raw_den: List[float] = []
        for i in range(n):
            start = max(0, i - k_period + 1)
            hh = max(float(highs[j]) for j in range(start, i + 1))
            ll = min(float(lows[j]) for j in range(start, i + 1))
            raw_num.append(float(closes[i]) - ll)
            raw_den.append(max(1e-12, hh - ll))

        sm_num = IndicatorEngine.sma(raw_num, slowing)
        sm_den = IndicatorEngine.sma(raw_den, slowing)
        k_vals = [max(0.0, min(100.0, 100.0 * (num / den))) for num, den in zip(sm_num, sm_den)]
        d_vals = IndicatorEngine.sma(k_vals, d_period)
        return k_vals, d_vals

    @staticmethod
    def ttm_squeeze(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        period: int = 20,
        bb_std: float = 2.0,
        kc_atr_mult: float = 1.5,
    ) -> Tuple[List[bool], List[float]]:
        """
        Detect TTM Volatility Squeeze (Bollinger Bands inside Keltner Channels)
        and compute momentum oscillator.
        """
        n = min(len(highs), len(lows), len(closes))
        if n == 0:
            return [], []

        bb_up, bb_mid, bb_low = IndicatorEngine.bollinger_bands(closes, period, bb_std)
        atr_vals = IndicatorEngine.atr(highs, lows, closes, period)
        kc_up = [m + kc_atr_mult * a for m, a in zip(bb_mid, atr_vals)]
        kc_low = [m - kc_atr_mult * a for m, a in zip(bb_mid, atr_vals)]

        squeeze_on = [bu < ku and bl > kl for bu, bl, ku, kl in zip(bb_up, bb_low, kc_up, kc_low)]
        momentum: List[float] = []
        for i in range(n):
            start = max(0, i - period + 1)
            hh = max(float(highs[j]) for j in range(start, i + 1))
            ll = min(float(lows[j]) for j in range(start, i + 1))
            mid_donchian = (hh + ll) * 0.5
            anchor = (mid_donchian + bb_mid[i]) * 0.5
            momentum.append(float(closes[i]) - anchor)

        return squeeze_on, momentum

    @staticmethod
    def vwap(bars: Sequence[Bar], window: int = 48) -> List[float]:
        """Compute rolling Volume-Weighted Average Price."""
        n = len(bars)
        if n == 0:
            return []
        out: List[float] = []
        for i in range(n):
            start = max(0, i - window + 1)
            pv_sum = 0.0
