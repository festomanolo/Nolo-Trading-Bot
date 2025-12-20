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


