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
