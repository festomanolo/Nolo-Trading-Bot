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


