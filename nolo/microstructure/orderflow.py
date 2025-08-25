"""
Real-Time Tick & Bar Order Flow Microstructure Engine.

Computes:
- Tick Rule & Intrabar Buying/Selling Pressure
- Cumulative Volume Delta (CVD) & CVD Slope / Divergence
- Volume-Synchronized Probability of Informed Trading (VPIN)
- Volume Profile Point of Control (POC), Value Area High (VAH), Value Area Low (VAL)
- Dynamic Spread Z-Score & Liquidity Vacuum Guard
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from nolo.types import Bar, Tick


@dataclass(frozen=True)
class OrderFlowSnapshot:
    """Snapshot of real-time order flow imbalance and liquidity conditions."""

    bar_delta: float
    cumulative_delta_slope: float
    buy_pressure_ratio: float
    vpin_toxicity: float
    poc_price: float
    vah_price: float
    val_price: float
    volume_surge_ratio: float
    bullish_cvd_divergence: bool
    bearish_cvd_divergence: bool
    spread_shock: bool


class OrderFlowAnalyzer:
    """Analyzes tick streams and OHLCV bars to extract institutional order flow metrics."""

    def __init__(self, profile_bins: int = 20) -> None:
        self.profile_bins = max(5, profile_bins)
        self._tick_deltas: List[float] = []

    def record_tick(self, prev_tick: Tick, curr_tick: Tick) -> float:
        """Apply Lee-Ready tick rule to classify tick volume as buyer or seller initiated."""
        mid_diff = curr_tick.mid - prev_tick.mid
        if mid_diff > 0:
            delta = curr_tick.volume
        elif mid_diff < 0:
            delta = -curr_tick.volume
        else:
            delta = 0.0
        self._tick_deltas.append(delta)
        if len(self._tick_deltas) > 500:
            self._tick_deltas = self._tick_deltas[-500:]
        return delta

    def analyze_bars(self, bars: Sequence[Bar], max_spread_points: float = 20.0) -> OrderFlowSnapshot:
        n = len(bars)
        if n < 10:
            p = bars[-1].close if n > 0 else 0.0
            return OrderFlowSnapshot(
                bar_delta=0.0,
                cumulative_delta_slope=0.0,
                buy_pressure_ratio=0.5,
                vpin_toxicity=0.2,
                poc_price=p,
                vah_price=p,
                val_price=p,
                volume_surge_ratio=1.0,
                bullish_cvd_divergence=False,
                bearish_cvd_divergence=False,
                spread_shock=False,
            )

        # Intrabar buying vs selling volume decomposition using close position within high-low range
        deltas: List[float] = []
        buy_vols: List[float] = []
        sell_vols: List[float] = []
        cvd: List[float] = []
        running_cvd = 0.0

        window_bars = bars[-min(n, 60) :]
        for b in window_bars:
            rng = b.range
            if rng <= 1e-12:
                buy_frac = 0.5
            else:
                buy_frac = max(0.0, min(1.0, (b.close - b.low) / rng))
            b_vol = b.volume * buy_frac
            s_vol = b.volume * (1.0 - buy_frac)
            delta = b_vol - s_vol
            buy_vols.append(b_vol)
            sell_vols.append(s_vol)
            deltas.append(delta)
            running_cvd += delta
            cvd.append(running_cvd)

        recent_vol_sum = sum(b.volume for b in window_bars[-10:])
        buy_pressure = (
            sum(buy_vols[-10:]) / recent_vol_sum if recent_vol_sum > 1e-9 else 0.5
        )

        # VPIN estimate: average |buy_vol - sell_vol| / total_vol over last 20 bars
        vpin_window = min(20, len(window_bars))
        vpin_vol = sum(b.volume for b in window_bars[-vpin_window:])
        vpin = (
            sum(abs(d) for d in deltas[-vpin_window:]) / vpin_vol
            if vpin_vol > 1e-9
            else 0.2
        )

        # CVD slope normalized by average volume
        avg_vol = sum(b.volume for b in window_bars[-20:]) / min(20, len(window_bars))
        cvd_change = cvd[-1] - cvd[-min(6, len(cvd))]
        cvd_slope = cvd_change / max(1e-6, avg_vol * 5.0)

        # Volume surge ratio
        vol_surge = window_bars[-1].volume / max(1e-6, avg_vol)

        # CVD Divergence detection over last 10 bars
        price_change = window_bars[-1].close - window_bars[-10].close
        cvd_10_change = cvd[-1] - cvd[-10]
        bull_div = price_change < 0 and cvd_10_change > 0 and buy_pressure > 0.52
        bear_div = price_change > 0 and cvd_10_change < 0 and buy_pressure < 0.48

        # Volume Profile POC, VAH, VAL
        poc, vah, val = self._compute_volume_profile(window_bars)

        spread_shock = window_bars[-1].spread_points > max_spread_points

        return OrderFlowSnapshot(
            bar_delta=deltas[-1],
            cumulative_delta_slope=cvd_slope,
            buy_pressure_ratio=buy_pressure,
            vpin_toxicity=max(0.0, min(1.0, vpin)),
            poc_price=poc,
