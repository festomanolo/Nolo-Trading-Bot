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

