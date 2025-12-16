"""Unit tests for Kalman Filter, Hurst Exponent, Entropy, Indicators, and OU Process."""

from __future__ import annotations

import math
import unittest

from nolo.quant.entropy import MarketEntropy
from nolo.quant.hurst import HurstAnalyzer
from nolo.quant.indicators import IndicatorEngine
from nolo.quant.kalman import KalmanTrendTracker
from nolo.quant.statistics import OrnsteinUhlenbeckEstimator, QuantitativeStatistics


class TestQuantModules(unittest.TestCase):
    def test_kalman_trend_tracker_uptrend(self) -> None:
        kf = KalmanTrendTracker(process_noise=1e-4, measurement_noise=1e-3)
        prices = [1.0800 + i * 0.0005 for i in range(40)]
        states = kf.filter_series(prices)
        self.assertEqual(len(states), 40)
        self.assertGreater(states[-1].velocity, 0.0)
        self.assertAlmostEqual(states[-1].level, prices[-1], places=2)

    def test_hurst_exponent_trending_vs_mean_reverting(self) -> None:
