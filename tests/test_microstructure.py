"""Unit tests for Smart Money Concepts (SMC), Order Flow, and Currency Strength."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from nolo.backtest.data_generator import RealisticForexDataGenerator
from nolo.microstructure.currency_strength import CurrencyStrengthMeter
from nolo.microstructure.orderflow import OrderFlowAnalyzer
from nolo.microstructure.smc import SmartMoneyAnalyzer
from nolo.types import Bar


class TestMicrostructure(unittest.TestCase):
    def test_smc_analyzer_detects_zones_and_structure(self) -> None:
        bars = RealisticForexDataGenerator.generate_bars("EURUSD", "M5", num_bars=120, seed=42)
        smc = SmartMoneyAnalyzer()
        snap = smc.analyze(bars)
        self.assertTrue(0.0 <= snap.dealing_range_position <= 1.0)
        self.assertGreater(snap.last_swing_high, 0.0)
        self.assertGreater(snap.last_swing_low, 0.0)

    def test_smc_bullish_fvg_detection(self) -> None:
        t0 = datetime(2025, 4, 1, 10, 0, tzinfo=timezone.utc)
