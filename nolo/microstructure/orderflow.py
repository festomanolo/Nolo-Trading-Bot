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
