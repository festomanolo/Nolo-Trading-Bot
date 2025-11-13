"""
Real-Time Event-Driven Trading Engine.

Orchestrates the complete lifecycle on every bar/tick:
1. Spread & Liquidity Shock Guard
2. Prop-Firm Daily & Total Trailing Drawdown Check
3. Open Trade Management (Break-Even, TP1/TP2 Partial Close, Smart ATR Trailing Stop)
4. Macroeconomic News Embargo Filter
5. Ensemble Signal Generation (Regime + SMC + OrderFlow + Neural Scorer + Bandit)
6. Currency Exposure & Correlation Guard
7. Bayesian Kelly Position Sizing & Order Execution
8. Online ML Feedback Loop on Trade Closure
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from nolo.config import BotConfig
from nolo.execution.mt5_bridge import MT5RealTimeBridge
from nolo.execution.paper_broker import RealisticECNBroker
from nolo.execution.trade_manager import SmartTradeManager
from nolo.intelligence.news_guard import EconomicCalendarGuard
from nolo.quant.indicators import IndicatorEngine
from nolo.risk.drawdown_guard import DrawdownAndPropGuard
from nolo.risk.exposure_manager import CurrencyExposureManager
from nolo.risk.position_sizer import PositionSizer
from nolo.strategies.ensemble import IntelligentEnsembleOrchestrator
from nolo.types import Bar, RegimeState


class RealTimeTradingEngine:
    """Full-stack autonomous real-time Forex trading engine."""

    def __init__(
        self,
        initial_balance: float = 10000.0,
        config: Optional[BotConfig] = None,
        enable_mt5_bridge: bool = False,
    ) -> None:
