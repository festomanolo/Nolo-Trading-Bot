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
        self.config = config or BotConfig()
        self.broker = RealisticECNBroker(initial_balance=initial_balance, config=self.config)
        self.orchestrator = IntelligentEnsembleOrchestrator(self.config)
        self.position_sizer = PositionSizer(self.config)
        self.drawdown_guard = DrawdownAndPropGuard(initial_balance=initial_balance, config=self.config)
        self.exposure_manager = CurrencyExposureManager(
            config=self.config, currency_meter=self.orchestrator.currency_meter
        )
        self.trade_manager = SmartTradeManager(self.config)
        self.news_guard = EconomicCalendarGuard()
        self.mt5_bridge = MT5RealTimeBridge() if enable_mt5_bridge else None

        self._last_trade_bar_idx: Dict[str, int] = {}
        self._bar_counter: Dict[str, int] = {}
        self.latest_regimes: Dict[str, RegimeState] = {}
        self.equity_curve: List[tuple[str, float]] = []

    def on_bar(
        self,
        symbol: str,
        bars: Sequence[Bar],
        htf_bars: Optional[Sequence[Bar]] = None,
    ) -> Optional[Dict[str, object]]:
        """Process a newly closed or updated bar for `symbol`."""
        if not bars:
            return None

        curr_bar = bars[-1]
        clean_sym = symbol.upper()[:6]
        spec = self.config.get_symbol_spec(clean_sym)

        idx = self._bar_counter.get(clean_sym, 0) + 1
        self._bar_counter[clean_sym] = idx

        half_spread = (curr_bar.spread_points * spec.point) * 0.5
        bid_close = curr_bar.close - half_spread
        ask_close = curr_bar.close + half_spread

        if len(bars) >= 35:
            highs = [b.high for b in bars[-30:]]
            lows = [b.low for b in bars[-30:]]
            closes = [b.close for b in bars[-30:]]
            atr_series = IndicatorEngine.atr(highs, lows, closes, self.config.indicators.atr_period)
            curr_atr = atr_series[-1] if atr_series else spec.pip_size * 10.0
            ref_atr = atr_series[-min(10, len(atr_series))] if atr_series else curr_atr

            # Check favorable excursion for TP1/TP2 partial scaling first
            for ticket, pos in list(self.broker.open_positions.items()):
