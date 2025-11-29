"""
Event-Driven Multi-Timeframe Backtester.

Replays historical or synthesized OHLCV bar streams chronologically without look-ahead bias,
maintaining synchronized Higher Timeframe (HTF) bars and full ECN execution accounting.
"""

from __future__ import annotations
