"""Configuration schemas and institutional preset profiles for Nolo Bot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from nolo.types import RiskModel, StrategyMode


@dataclass
class SymbolSpec:
    """Instrument specification for accurate pip, tick, and lot sizing."""

    symbol: str
    digits: int = 5
