"""
Intelligent Ensemble Strategy Orchestrator.

Coordinates:
- Multi-Factor Regime Detection (`AdaptiveRegimeEngine`)
- Smart Money Concepts (`SmartMoneyAnalyzer`)
- Real-Time Order Flow (`OrderFlowAnalyzer`)
- Multi-Currency Strength (`CurrencyStrengthMeter`)
- Contextual Bandit Strategy Weighting (`RegimeContextualBandit`)
- Online Neural Signal Scoring (`AdaptiveNeuralScorer`)
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from nolo.config import BotConfig
from nolo.intelligence.bandit_allocator import RegimeContextualBandit
from nolo.intelligence.neural_scorer import AdaptiveNeuralScorer
from nolo.intelligence.regime import AdaptiveRegimeEngine
from nolo.microstructure.currency_strength import CurrencyStrengthMeter
from nolo.microstructure.orderflow import OrderFlowAnalyzer
from nolo.microstructure.smc import SmartMoneyAnalyzer
from nolo.strategies.base import BaseStrategy, StrategyContext
from nolo.strategies.mean_reversion import OrnsteinUhlenbeckRangeStrategy
from nolo.strategies.smc_breakout import SMCLiquidityBreakoutStrategy
from nolo.strategies.trend_following import KalmanTrendStrategy
from nolo.strategies.volatility_momentum import VolatilitySqueezeMomentumStrategy
from nolo.types import Bar, RegimeType, Signal, StrategyMode


class IntelligentEnsembleOrchestrator:
    """Master AI/Quant orchestrator selecting and scoring the best signal for current market conditions."""

    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()
        self.regime_engine = AdaptiveRegimeEngine(self.config.indicators)
        self.smc_analyzer = SmartMoneyAnalyzer(self.config.smc)
        self.orderflow_analyzer = OrderFlowAnalyzer()
        self.currency_meter = CurrencyStrengthMeter()
        self.neural_scorer = AdaptiveNeuralScorer(self.config.ml)

        self.trend_strategy = KalmanTrendStrategy(self.config)
        self.range_strategy = OrnsteinUhlenbeckRangeStrategy(self.config)
        self.breakout_strategy = SMCLiquidityBreakoutStrategy(self.config)
        self.volatility_strategy = VolatilitySqueezeMomentumStrategy(self.config)

        self.all_strategies: List[BaseStrategy] = [
            self.trend_strategy,
            self.range_strategy,
            self.breakout_strategy,
            self.volatility_strategy,
        ]
        self.bandit = RegimeContextualBandit(
            strategy_names=[s.name for s in self.all_strategies],
            exploration_c=self.config.ml.bandit_exploration_c,
            discount_gamma=self.config.ml.bandit_discount_gamma,
        )

    def generate_signal(
        self,
        symbol: str,
        bars: Sequence[Bar],
        htf_bars: Optional[Sequence[Bar]] = None,
    ) -> Optional[Signal]:
        """Run full quantitative & ML pipeline on `bars` and emit the highest-edge calibrated Signal."""
        if len(bars) < 35:
            return None

        spec = self.config.get_symbol_spec(symbol)
        closes = [b.close for b in bars]
        self.currency_meter.update_pair_prices(symbol, closes)

        regime_state = self.regime_engine.detect(bars)
        smc_snap = self.smc_analyzer.analyze(bars)
        oflow_snap = self.orderflow_analyzer.analyze_bars(bars, max_spread_points=spec.max_spread_points)
        if oflow_snap.spread_shock:
            return None

        curr_div = (
            self.currency_meter.pair_divergence_score(symbol)
            if self.config.use_currency_strength
            else 0.0
        )

        ctx = StrategyContext(
            symbol=symbol,
            bars=bars,
            htf_bars=htf_bars,
            regime_state=regime_state,
