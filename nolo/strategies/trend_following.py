"""
Kalman + SuperTrend + Ichimoku Cloud Multi-Timeframe Trend Following Strategy.

Upgrades the v3.5 Trend Following logic with:
- State-space Kalman velocity confirmation
- Fixed SuperTrend band ratcheting
- Ichimoku Kumo Cloud + Tenkan/Kijun cross boost
- Order Flow Cumulative Volume Delta (CVD) alignment
"""

from __future__ import annotations

from typing import Dict, List, Optional

from nolo.quant.indicators import IndicatorEngine
from nolo.strategies.base import BaseStrategy, StrategyContext
