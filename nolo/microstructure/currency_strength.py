"""
Multi-Currency Relative Strength Index (CSI) & Cross-Pair Correlation Matrix.

Tracks real-time relative performance across the G8 currencies:
EUR, USD, GBP, JPY, AUD, CAD, CHF, NZD.
Enables trading high-divergence currency pairs (strongest base vs weakest quote)
and blocks over-concentrated correlated exposure.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from nolo.quant.statistics import QuantitativeStatistics

MAJOR_CURRENCIES: Tuple[str, ...] = ("EUR", "USD", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD")


class CurrencyStrengthMeter:
    """Computes G8 currency strength scores and cross-pair correlation matrices."""

    def __init__(self, lookback: int = 20) -> None:
        self.lookback = max(5, lookback)
