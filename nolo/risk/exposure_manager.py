"""
Multi-Currency Portfolio Exposure & Cross-Pair Correlation Guard.

Prevents hidden risk concentration such as going simultaneously long EURUSD, GBPUSD,
and AUDUSD (which triples short-USD risk).
"""

from __future__ import annotations
