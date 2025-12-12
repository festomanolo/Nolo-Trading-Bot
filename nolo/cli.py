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
