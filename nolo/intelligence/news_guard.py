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

    def add_event(self, event: NewsEvent) -> None:
        self._events.append(event)

    def clear_events(self) -> None:
        self._events.clear()

    def is_embargoed(self, symbol: str, current_time: datetime) -> tuple[bool, Optional[str]]:
        """
        Check if `symbol` (e.g. 'EURUSD') is inside a pre-news or post-news embargo window,
        or inside the First-Friday NFP release window (13:15 - 14:00 UTC).
        """
        clean = symbol.upper()[:6]
        base = clean[:3]
        quote = clean[3:6]

        for ev in self._events:
            if ev.impact.upper() not in ("HIGH", "CRITICAL"):
                continue
            if ev.currency.upper() not in (base, quote, "ALL", "USD"):
                continue
            start_win = ev.timestamp - timedelta(minutes=ev.pre_embargo_minutes)
            end_win = ev.timestamp + timedelta(minutes=ev.post_embargo_minutes)
            if start_win <= current_time <= end_win:
                return True, f"{ev.currency} {ev.title} ({ev.impact})"

        # Built-in structural rule: US Non-Farm Payrolls (First Friday of month 13:15-14:00 UTC)
        if "USD" in (base, quote):
            if current_time.weekday() == 4 and 1 <= current_time.day <= 7:
                if current_time.hour == 13 and 15 <= current_time.minute <= 59:
                    return True, "USD Non-Farm Payrolls (Automatic First-Friday Guard)"

        return False, None

    def risk_scaling_factor(self, symbol: str, current_time: datetime) -> float:
