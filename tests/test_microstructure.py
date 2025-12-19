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
        bars = []
        for i in range(20):
            bars.append(
                Bar("EURUSD", "M5", t0 + timedelta(minutes=5 * i), 1.0800, 1.0805, 1.0795, 1.0801, 100.0)
            )
        # Create explicit 3-bar bullish impulse FVG
        bars.append(Bar("EURUSD", "M5", t0 + timedelta(minutes=105), 1.0802, 1.0804, 1.0798, 1.0799, 120.0))
        bars.append(Bar("EURUSD", "M5", t0 + timedelta(minutes=110), 1.0800, 1.0835, 1.0800, 1.0832, 450.0))
        bars.append(Bar("EURUSD", "M5", t0 + timedelta(minutes=115), 1.0830, 1.0838, 1.0815, 1.0820, 200.0))

        smc = SmartMoneyAnalyzer()
        snap = smc.analyze(bars)
        self.assertTrue(len(snap.active_zones) >= 1)

    def test_orderflow_and_volume_profile(self) -> None:
        bars = RealisticForexDataGenerator.generate_bars("GBPUSD", "M5", num_bars=80, seed=99)
        oflow = OrderFlowAnalyzer()
