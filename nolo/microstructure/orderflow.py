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
