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
