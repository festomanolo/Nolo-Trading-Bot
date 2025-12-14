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
    print(f"=== NOLO TRADING BOT v4.0 BACKTEST REPORT ({symbol}) ===")
    print(f"Initial Balance : ${rep.initial_balance:,.2f}")
    print(f"Final Balance   : ${rep.final_balance:,.2f} (Net: ${rep.net_profit:+,.2f} | ROI: {rep.roi_pct:+.2f}%)")
    print(f"Total Trades    : {rep.total_trades} (Wins: {rep.winning_trades}, Losses: {rep.losing_trades})")
    print(f"Win Rate        : {rep.win_rate_pct:.2f}%")
    print(f"Profit Factor   : {rep.profit_factor:.3f}")
    print(f"Sharpe / Sortino: {rep.sharpe_ratio:.2f} / {rep.sortino_ratio:.2f}")
    print(f"Max Drawdown    : {rep.max_drawdown_pct:.2f}%")
    print(f"MT5 OnTester    : {rep.on_tester_score:.2f}")
    print(f"Regime Split    : {json.dumps(rep.regime_breakdown)}")
    print(f"Strategy Split  : {json.dumps(rep.strategy_breakdown)}")
    return 0


def cmd_montecarlo(symbol: str, num_bars: int, iterations: int, seed: int) -> int:
    start_price = 152.50 if "JPY" in symbol.upper() else 1.0850
    bars = RealisticForexDataGenerator.generate_bars(
        symbol=symbol, timeframe="M5", num_bars=num_bars, start_price=start_price, seed=seed
    )
    bt = EventDrivenBacktester(initial_balance=10000.0, config=BotConfig())
    result = bt.run(bars)
    mc = MonteCarloStressTester.run_simulations(10000.0, result.trades, iterations=iterations, seed=seed)
    print(f"=== MONTE CARLO STRESS TEST ({iterations} runs on {symbol}) ===")
    print(f"Median Net Profit     : ${mc.median_net_profit:+,.2f}")
    print(f"5th - 95th Percentile : ${mc.p5_net_profit:+,.2f} to ${mc.p95_net_profit:+,.2f}")
    print(f"Median Max Drawdown   : {mc.median_max_drawdown_pct:.2f}%")
    print(f"95% VaR Max Drawdown  : {mc.var_95_max_drawdown_pct:.2f}%")
    print(f"99% CVaR Max Drawdown : {mc.cvar_99_max_drawdown_pct:.2f}%")
    print(f"Probability of Profit : {mc.probability_of_profit_pct:.2f}%")
    return 0


def cmd_optimize(symbol: str, num_bars: int, seed: int) -> int:
    start_price = 152.50 if "JPY" in symbol.upper() else 1.0850
    bars = RealisticForexDataGenerator.generate_bars(
        symbol=symbol, timeframe="M5", num_bars=num_bars, start_price=start_price, seed=seed
    )
    opt = WalkForwardOptimizer()
    candidates = opt.optimize(bars)
    print(f"=== WALK-FORWARD OPTIMIZATION TOP CANDIDATES ({symbol}) ===")
    for idx, c in enumerate(candidates[:5], start=1):
