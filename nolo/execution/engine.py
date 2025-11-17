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
                if pos.symbol != clean_sym:
                    continue
                fav_bid = (curr_bar.high - half_spread) if pos.side.value == "BUY" else bid_close
                fav_ask = (curr_bar.low + half_spread) if pos.side.value == "SELL" else ask_close
                actions = self.trade_manager.manage_position(pos, fav_bid, fav_ask, curr_atr, ref_atr)
                for act in actions:
                    if act.action_type == "PARTIAL_CLOSE" and act.close_lots > 0:
                        self.broker.partial_close(
                            ticket, act.close_lots, pos.current_price, curr_bar.timestamp, act.reason
                        )
                    elif act.action_type == "MODIFY_SL" and act.new_sl is not None:
                        self.broker.modify_stop_loss(ticket, act.new_sl)

        # Process intrabar SL/TP hits on remaining position
        closed_records = self.broker.process_bar_stops(curr_bar)
        for rec in closed_records:
            self._handle_closed_trade(rec)

        # Update drawdown guard & equity curve
        self.drawdown_guard.on_new_bar_or_tick(
            curr_bar.timestamp, self.broker.balance, self.broker.equity
        )
        self.equity_curve.append((curr_bar.timestamp.isoformat(), round(self.broker.equity, 2)))

        if len(bars) < 35:
            return None

        # 4. Spread Guard
        if curr_bar.spread_points > spec.max_spread_points:
            return {"status": "SKIPPED_SPREAD", "spread": curr_bar.spread_points}

        # 5. Check Drawdown, Daily Trade Limit, Cooldown, and Rollover Guard
        last_idx = self._last_trade_bar_idx.get(clean_sym, -999)
        bars_since = idx - last_idx
        allowed, block_reason = self.drawdown_guard.can_open_trade(
            curr_bar.timestamp, self.broker.balance, self.broker.equity, bars_since
        )
        if not allowed:
            return {"status": "BLOCKED_RISK", "reason": block_reason}

        # 6. Check Economic Calendar News Filter
        if self.config.use_news_filter:
            embargoed, news_reason = self.news_guard.is_embargoed(clean_sym, curr_bar.timestamp)
            if embargoed:
                return {"status": "BLOCKED_NEWS", "reason": news_reason}

        # 7. Run Ensemble Signal Orchestrator
        signal = self.orchestrator.generate_signal(clean_sym, bars, htf_bars)
        regime_state = self.orchestrator.regime_engine.detect(bars)
        self.latest_regimes[clean_sym] = regime_state

        if self.mt5_bridge is not None:
            self.mt5_bridge.publish_signal_and_regime(clean_sym, regime_state, signal)

        if signal is None:
            return {"status": "NO_SIGNAL", "regime": regime_state.regime.value}

        # 8. Check Portfolio Exposure & Cross-Pair Correlation Guard
        can_add, exp_reason = self.exposure_manager.can_add_position(
            clean_sym, signal.side, list(self.broker.open_positions.values())
        )
        if not can_add:
            return {"status": "BLOCKED_EXPOSURE", "reason": exp_reason}

        # 9. Compute Position Size via Bayesian Kelly + Equity Curve Throttle
