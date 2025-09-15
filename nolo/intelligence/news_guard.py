"""
Real-Time Macroeconomic News Calendar Filter & Volatility Embargo Engine.

Replaces the placeholder `IsHighImpactNews()` in v3.5 with a full currency-aware
embargo engine supporting scheduled macro events (NFP, CPI, FOMC, ECB, BOE, BOJ, GDP, PMI)
plus recurring intraday session fix/rollover volatility windows.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class NewsEvent:
    """Scheduled macroeconomic calendar event."""

    title: str
    currency: str
    timestamp: datetime
    impact: str = "HIGH"  # "HIGH", "MEDIUM", "LOW"
    pre_embargo_minutes: int = 30
    post_embargo_minutes: int = 30


class EconomicCalendarGuard:
    """Evaluates whether trading on a given currency pair is restricted by macro news."""

    def __init__(self, events: Optional[Sequence[NewsEvent]] = None) -> None:
        self._events: List[NewsEvent] = list(events) if events else []

