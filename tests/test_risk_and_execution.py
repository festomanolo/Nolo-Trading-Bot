"""Unit tests for Risk Sizing, Drawdown Guard, Exposure Manager, Backtester, and CLI."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from nolo.backtest.backtester import EventDrivenBacktester
from nolo.backtest.data_generator import RealisticForexDataGenerator
from nolo.backtest.monte_carlo import MonteCarloStressTester
from nolo.config import BotConfig
from nolo.risk.drawdown_guard import DrawdownAndPropGuard
from nolo.risk.exposure_manager import CurrencyExposureManager
from nolo.risk.position_sizer import PositionSizer
from nolo.types import OrderSide, Position, RegimeType


class TestRiskExecutionAndBacktest(unittest.TestCase):
    def test_position_sizer_respects_broker_lot_limits(self) -> None:
        cfg = BotConfig()
        sizer = PositionSizer(cfg)
        spec = cfg.get_symbol_spec("EURUSD")
        eff_pct = sizer.compute_effective_risk_pct(signal_win_prob=0.68, risk_multiplier=1.2)
        lots = sizer.calculate_lots(
            account_balance=10000.0,
            stop_loss_distance_price=0.0020,
            spec=spec,
            effective_risk_pct=eff_pct,
        )
        self.assertGreaterEqual(lots, spec.min_lot)
        self.assertLessEqual(lots, spec.max_lot)

    def test_drawdown_guard_triggers_on_daily_loss(self) -> None:
        cfg = BotConfig()
        guard = DrawdownAndPropGuard(initial_balance=10000.0, config=cfg)
        now = datetime(2025, 6, 10, 14, 0, tzinfo=timezone.utc)
        ok, _ = guard.can_open_trade(now, balance=10000.0, equity=9400.0, bars_since_last_trade=10)
        self.assertFalse(ok)

    def test_currency_exposure_blocks_correlated_positions(self) -> None:
        cfg = BotConfig()
        mgr = CurrencyExposureManager(cfg)
        pos = Position(
            ticket=1,
            symbol="EURUSD",
            side=OrderSide.BUY,
            open_time=datetime(2025, 6, 10, 10, 0, tzinfo=timezone.utc),
            open_price=1.0850,
            current_price=1.0860,
            initial_lots=0.5,
            current_lots=0.5,
            stop_loss=1.0830,
            take_profit=1.0900,
            initial_stop_loss=1.0830,
            strategy_name="KalmanTrendFollowing",
            regime=RegimeType.TREND_UP,
        )
        # Same symbol must be blocked
        allowed, _ = mgr.can_add_position("EURUSD", OrderSide.BUY, [pos])
        self.assertFalse(allowed)

    def test_full_event_driven_backtest_and_monte_carlo(self) -> None:
        bars = RealisticForexDataGenerator.generate_bars("EURUSD", "M5", num_bars=450, seed=2025)
        bt = EventDrivenBacktester(initial_balance=10000.0)
        res = bt.run(bars)
        self.assertGreater(res.report.total_trades, 0)
        self.assertGreater(res.report.final_balance, 0.0)

        mc = MonteCarloStressTester.run_simulations(10000.0, res.trades, iterations=100, seed=2025)
        self.assertEqual(mc.iterations, 100)
        self.assertGreaterEqual(mc.cvar_99_max_drawdown_pct, mc.median_max_drawdown_pct)


if __name__ == "__main__":
    unittest.main()
