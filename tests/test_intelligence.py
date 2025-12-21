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

