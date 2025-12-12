"""
Command-Line Interface for Nolo Trading Bot v4.0.

Usage:
    python3 -m nolo.cli backtest --symbol EURUSD --bars 600
    python3 -m nolo.cli montecarlo --symbol EURUSD --iterations 500
    python3 -m nolo.cli optimize --symbol EURUSD
    python3 -m nolo.cli multi-pair
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from nolo.backtest.backtester import EventDrivenBacktester
from nolo.backtest.data_generator import RealisticForexDataGenerator
from nolo.backtest.monte_carlo import MonteCarloStressTester
from nolo.backtest.walk_forward import WalkForwardOptimizer
from nolo.config import BotConfig


def cmd_backtest(symbol: str, num_bars: int, seed: int) -> int:
    start_price = 152.50 if "JPY" in symbol.upper() else 1.0850
    bars = RealisticForexDataGenerator.generate_bars(
        symbol=symbol, timeframe="M5", num_bars=num_bars, start_price=start_price, seed=seed
    )
    bt = EventDrivenBacktester(initial_balance=10000.0, config=BotConfig())
    result = bt.run(bars)
    rep = result.report
