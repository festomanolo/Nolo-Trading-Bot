"""Abstract base class and shared evaluation context for all alpha strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from nolo.config import BotConfig
from nolo.microstructure.orderflow import OrderFlowSnapshot
from nolo.microstructure.smc import SMCSnapshot
from nolo.types import Bar, OrderSide, RegimeState, Signal


@dataclass
