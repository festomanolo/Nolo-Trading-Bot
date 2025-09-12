"""
Contextual Bandit Meta-Strategy Allocator (Discounted UCB1 + Bayesian Beta-Bernoulli).

Tracks strategy performance conditioned on each market regime and dynamically
scales capital & confidence weights toward the best-performing alpha strategies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

from nolo.types import RegimeType


@dataclass
class ArmStats:
    """Discounted reward statistics for a (regime, strategy) arm."""

    alpha: float = 2.0  # Beta prior wins
    beta: float = 2.0   # Beta prior losses
    pulls: float = 1.0
    cum_r: float = 0.5

