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
        self._pair_prices: Dict[str, List[float]] = {}

    def update_pair_prices(self, symbol: str, closes: Sequence[float]) -> None:
        clean = symbol.upper()[:6]
        self._pair_prices[clean] = [float(x) for x in closes[-max(100, self.lookback * 3) :]]

    def compute_strengths(self) -> Dict[str, float]:
        """
        Return normalized strength scores in [-100, +100] for each major currency.
        """
        scores: Dict[str, List[float]] = {c: [] for c in MAJOR_CURRENCIES}

        for pair, series in self._pair_prices.items():
            if len(pair) < 6 or len(series) < 2:
                continue
            base = pair[:3]
            quote = pair[3:6]
            w = min(len(series) - 1, self.lookback)
            p0 = max(1e-9, series[-1 - w])
            p1 = series[-1]
            pct_return = ((p1 - p0) / p0) * 100.0
            scaled = max(-100.0, min(100.0, pct_return * 40.0))

            if base in scores:
                scores[base].append(scaled)
            if quote in scores:
                scores[quote].append(-scaled)

        result: Dict[str, float] = {}
        for c in MAJOR_CURRENCIES:
            vals = scores[c]
            result[c] = sum(vals) / len(vals) if vals else 0.0
        return result

    def pair_divergence_score(self, symbol: str) -> float:
        """
        Return base_strength - quote_strength for `symbol`.
        Positive values favor BUY; negative values favor SELL.
        """
        clean = symbol.upper()[:6]
        base = clean[:3]
        quote = clean[3:6]
        strengths = self.compute_strengths()
        return strengths.get(base, 0.0) - strengths.get(quote, 0.0)

    def correlation_between(self, symbol_a: str, symbol_b: str, window: int = 30) -> float:
        """Compute rolling return correlation between two currency pairs."""
        a_clean = symbol_a.upper()[:6]
        b_clean = symbol_b.upper()[:6]
        if a_clean == b_clean:
            return 1.0

        sa = self._pair_prices.get(a_clean, [])
        sb = self._pair_prices.get(b_clean, [])
        n = min(len(sa), len(sb), window + 1)
        if n < 5:
            return self._structural_currency_correlation(a_clean, b_clean)

        ret_a = [(sa[-n + i] - sa[-n + i - 1]) / max(1e-9, sa[-n + i - 1]) for i in range(1, n)]
        ret_b = [(sb[-n + i] - sb[-n + i - 1]) / max(1e-9, sb[-n + i - 1]) for i in range(1, n)]
        return QuantitativeStatistics.pearson_correlation(ret_a, ret_b)

    @staticmethod
