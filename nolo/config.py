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
    commission_per_lot: float = 7.0
    max_spread_points: int = 20

    @property
    def base_currency(self) -> str:
        return self.symbol[:3].upper()

    @property
    def quote_currency(self) -> str:
        return self.symbol[3:6].upper()


DEFAULT_SYMBOL_SPECS: Dict[str, SymbolSpec] = {
    "EURUSD": SymbolSpec("EURUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "GBPUSD": SymbolSpec("GBPUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "USDJPY": SymbolSpec("USDJPY", digits=3, point=0.001, pip_size=0.01, tick_size=0.001, tick_value=0.68),
    "AUDUSD": SymbolSpec("AUDUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "USDCAD": SymbolSpec("USDCAD", digits=5, point=0.00001, pip_size=0.0001, tick_value=0.74),
    "USDCHF": SymbolSpec("USDCHF", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.12),
    "NZDUSD": SymbolSpec("NZDUSD", digits=5, point=0.00001, pip_size=0.0001, tick_value=1.0),
    "EURJPY": SymbolSpec("EURJPY", digits=3, point=0.001, pip_size=0.01, tick_size=0.001, tick_value=0.68),
    "GBPJPY": SymbolSpec("GBPJPY", digits=3, point=0.001, pip_size=0.01, tick_size=0.001, tick_value=0.68, max_spread_points=30),
    "XAUUSD": SymbolSpec("XAUUSD", digits=2, point=0.01, pip_size=0.10, tick_size=0.01, tick_value=1.0, contract_size=100.0, max_spread_points=35),
}


@dataclass
class IndicatorConfig:
    """Parameters for technical, statistical, and state-space indicators."""

    fast_ma_period: int = 8
    slow_ma_period: int = 21
