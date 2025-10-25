"""
Multi-Currency Portfolio Exposure & Cross-Pair Correlation Guard.

Prevents hidden risk concentration such as going simultaneously long EURUSD, GBPUSD,
and AUDUSD (which triples short-USD risk).
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from nolo.config import BotConfig
from nolo.microstructure.currency_strength import CurrencyStrengthMeter
from nolo.types import OrderSide, Position


class CurrencyExposureManager:
    """Enforces net single-currency risk limits and pairwise correlation caps."""

    def __init__(
        self,
        config: Optional[BotConfig] = None,
        currency_meter: Optional[CurrencyStrengthMeter] = None,
    ) -> None:
        self.config = config or BotConfig()
        self.currency_meter = currency_meter or CurrencyStrengthMeter()

    def compute_net_currency_exposure_lots(
        self, open_positions: Sequence[Position]
    ) -> Dict[str, float]:
        """Compute signed net lot exposure per currency (+lots = net long, -lots = net short)."""
        exposure: Dict[str, float] = {}
        for pos in open_positions:
            clean = pos.symbol.upper()[:6]
            if len(clean) < 6:
                continue
            base, quote = clean[:3], clean[3:6]
            sign = 1.0 if pos.side == OrderSide.BUY else -1.0
            exposure[base] = exposure.get(base, 0.0) + sign * pos.current_lots
            exposure[quote] = exposure.get(quote, 0.0) - sign * pos.current_lots
        return exposure

    def can_add_position(
        self,
        symbol: str,
        side: OrderSide,
        open_positions: Sequence[Position],
    ) -> tuple[bool, Optional[str]]:
