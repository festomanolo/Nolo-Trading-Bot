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

