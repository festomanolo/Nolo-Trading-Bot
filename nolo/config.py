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
    point: float = 0.00001
    pip_size: float = 0.0001
    tick_size: float = 0.00001
    tick_value: float = 1.0
    contract_size: float = 100000.0
    min_lot: float = 0.01
    max_lot: float = 100.0
    lot_step: float = 0.01
