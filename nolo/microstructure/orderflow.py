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
