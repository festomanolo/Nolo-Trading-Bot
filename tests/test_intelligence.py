"""Unit tests for Regime Detection, Neural Signal Scorer, Contextual Bandit, and News Guard."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from nolo.backtest.data_generator import RealisticForexDataGenerator
from nolo.intelligence.bandit_allocator import RegimeContextualBandit
from nolo.intelligence.neural_scorer import AdaptiveNeuralScorer
from nolo.intelligence.news_guard import EconomicCalendarGuard, NewsEvent
from nolo.intelligence.regime import AdaptiveRegimeEngine
from nolo.types import RegimeType


class TestIntelligenceModules(unittest.TestCase):
    def test_regime_engine_probabilities_sum_to_one(self) -> None:
        bars = RealisticForexDataGenerator.generate_bars("EURUSD", "M5", num_bars=90, seed=101)
        engine = AdaptiveRegimeEngine()
        state = engine.detect(bars)
        self.assertIn(state.regime, list(RegimeType))
        self.assertAlmostEqual(sum(state.probabilities.values()), 1.0, places=5)

    def test_neural_scorer_online_learning_improves_prediction(self) -> None:
        scorer = AdaptiveNeuralScorer()
        strong_features = {
            "trend_alignment": 1.0,
            "kalman_velocity": 0.9,
            "hurst_persistence": 0.6,
            "efficiency_ratio": 0.8,
            "adx_strength": 0.7,
            "rsi_confluence": 0.8,
            "macd_impulse": 0.7,
            "smc_zone_confluence": 0.9,
            "orderflow_pressure": 0.8,
            "currency_divergence": 0.6,
            "htf_confirmation": 1.0,
            "volatility_quality": 0.85,
        }
        p_initial = scorer.predict_probability(strong_features)
        for _ in range(10):
            scorer.partial_fit(strong_features, is_win=True, r_multiple=2.0)
        p_after = scorer.predict_probability(strong_features)
        self.assertGreater(p_after, p_initial)
        self.assertGreater(p_after, 0.75)

    def test_contextual_bandit_shifts_weights_to_winner(self) -> None:
        bandit = RegimeContextualBandit(["StratA", "StratB"])
        for _ in range(12):
            bandit.record_outcome(RegimeType.TREND_UP, "StratA", is_win=True, r_multiple=2.2)
            bandit.record_outcome(RegimeType.TREND_UP, "StratB", is_win=False, r_multiple=-1.0)
        w_a = bandit.get_strategy_weight(RegimeType.TREND_UP, "StratA")
        w_b = bandit.get_strategy_weight(RegimeType.TREND_UP, "StratB")
        self.assertGreater(w_a, w_b)

    def test_economic_calendar_guard_blocks_high_impact_and_nfp(self) -> None:
        ev_time = datetime(2025, 5, 7, 18, 0, tzinfo=timezone.utc)
        guard = EconomicCalendarGuard(
            [NewsEvent("FOMC Rate Decision", "USD", ev_time, impact="HIGH")]
        )
        blocked, reason = guard.is_embargoed("EURUSD", datetime(2025, 5, 7, 17, 45, tzinfo=timezone.utc))
        self.assertTrue(blocked)
        self.assertIn("FOMC", reason or "")

        # First Friday NFP check (May 2, 2025 was a Friday, 13:30 UTC)
        nfp_blocked, _ = guard.is_embargoed("GBPUSD", datetime(2025, 5, 2, 13, 30, tzinfo=timezone.utc))
        self.assertTrue(nfp_blocked)


if __name__ == "__main__":
    unittest.main()
