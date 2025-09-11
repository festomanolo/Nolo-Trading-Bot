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


