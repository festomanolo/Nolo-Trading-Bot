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
        trending = [1.0500 + (i**1.15) * 0.0003 for i in range(80)]
        oscillating = [1.0800 + (0.0020 if i % 2 == 0 else -0.0020) for i in range(80)]
        h_trend = HurstAnalyzer.compute_hurst(trending)
        h_osc = HurstAnalyzer.compute_hurst(oscillating)
        self.assertGreater(h_trend, h_osc)
        self.assertTrue(0.05 <= h_trend <= 0.95)
        self.assertTrue(0.05 <= h_osc <= 0.95)

    def test_entropy_and_efficiency_ratio(self) -> None:
        clean_trend = [1.1000 + i * 0.0004 for i in range(30)]
        choppy = [1.1000 + (0.0010 if i % 2 == 0 else -0.0010) for i in range(30)]
        er_trend = MarketEntropy.efficiency_ratio(clean_trend, period=14)
        er_chop = MarketEntropy.efficiency_ratio(choppy, period=14)
        self.assertAlmostEqual(er_trend, 1.0, places=5)
        self.assertLess(er_chop, 0.25)

    def test_indicators_shapes_and_bounds(self) -> None:
        n = 60
        closes = [1.0800 + math.sin(i * 0.25) * 0.0050 + i * 0.0001 for i in range(n)]
        highs = [c + 0.0008 for c in closes]
        lows = [c - 0.0008 for c in closes]

        rsi = IndicatorEngine.rsi(closes, 14)
        self.assertEqual(len(rsi), n)
        self.assertTrue(all(0.0 <= x <= 100.0 for x in rsi))

        adx, pdi, mdi = IndicatorEngine.adx(highs, lows, closes, 14)
        self.assertEqual(len(adx), n)
        self.assertEqual(len(pdi), n)
        self.assertEqual(len(mdi), n)

        st_line, st_dir = IndicatorEngine.supertrend(highs, lows, closes, 14, 2.5)
        self.assertEqual(len(st_line), n)
        self.assertTrue(all(d in (-1, 1) for d in st_dir))

        sq_on, sq_mom = IndicatorEngine.ttm_squeeze(highs, lows, closes)
        self.assertEqual(len(sq_on), n)
        self.assertEqual(len(sq_mom), n)

    def test_ornstein_uhlenbeck_fit_and_correlation(self) -> None:
