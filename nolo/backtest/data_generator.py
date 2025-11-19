"""
Regime-Switching Stochastic Forex Market Data Generator & Historical CSV Loader.

Generates realistic multi-regime OHLCV bars exhibiting:
- Persistent trending phases (positive drift + low entropy)
- Mean-reverting Ornstein-Uhlenbeck consolidation ranges
- Institutional liquidity sweeps and volatility breakouts
- Intraday London/NY volume & spread seasonality
"""

from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta, timezone
