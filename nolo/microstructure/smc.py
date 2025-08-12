"""
Institutional Smart Money Concepts (SMC) & Price Action Microstructure Engine.

Detects:
1. Fractal Swing Highs & Swing Lows
2. Break of Structure (BOS) & Change of Character (CHoCH)
3. Bullish & Bearish Order Blocks (OB) with impulse validation and mitigation tracking
4. Bullish & Bearish Fair Value Gaps (FVG / 3-bar imbalances)
5. Buy-Side & Sell-Side Liquidity Sweeps (Stop Hunts / Turtle Soup reversals)
6. Dealing Range Premium / Equilibrium / Discount positioning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from nolo.config import SMCConfig
from nolo.quant.indicators import IndicatorEngine
from nolo.types import Bar, MarketStructureBias, SMCZone, SMCZoneType


@dataclass
class SMCSnapshot:
    """Complete institutional structure snapshot at the current bar."""

    structure_bias: MarketStructureBias
    last_swing_high: float
    last_swing_low: float
    dealing_range_position: float  # 0.0 = extreme discount, 0.5 = equilibrium, 1.0 = extreme premium
    in_bullish_ob: bool
    in_bearish_ob: bool
    in_bullish_fvg: bool
    in_bearish_fvg: bool
    bullish_liquidity_sweep: bool
    bearish_liquidity_sweep: bool
    active_zones: List[SMCZone] = field(default_factory=list)
    nearest_support: float = 0.0
    nearest_resistance: float = 0.0


class SmartMoneyAnalyzer:
    """Analyzes OHLCV bars for institutional Smart Money footprints."""

    def __init__(self, config: Optional[SMCConfig] = None) -> None:
        self.config = config or SMCConfig()

    def analyze(self, bars: Sequence[Bar]) -> SMCSnapshot:
