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
