"""
Monte Carlo Trade Sequence Permutation & Drawdown Stress Tester.

Evaluates tail-risk robustness by reshuffling realized trade PnLs with replacement
across N simulations to estimate 95% and 99% Value-at-Risk (VaR) and Conditional VaR (CVaR)
of maximum drawdown.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence

from nolo.types import TradeRecord

