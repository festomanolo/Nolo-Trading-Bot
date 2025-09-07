"""
Online Adaptive Neural & Logistic Ensemble Signal Scorer.

Combines:
1. Calibrated Domain Expert Prior Weights across 12 normalized quantitative features
2. Online 2-Layer Neural Perceptron with LeakyReLU hidden activations & L2 weight decay
3. Exponentially weighted online updates (`partial_fit`) from realized trade outcomes
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from nolo.config import MLConfig

