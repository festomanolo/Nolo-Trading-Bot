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
