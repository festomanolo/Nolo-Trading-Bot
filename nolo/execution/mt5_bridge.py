"""
MetaTrader 5 Real-Time Bridge (Native Python `MetaTrader5` API + JSON/Socket Telemetry Pipe).

Allows Nolo Bot's Python AI/Quant Engine to:
1. Connect directly to a running MetaTrader 5 terminal when the `MetaTrader5` package is available
2. Exchange real-time JSON signal & regime telemetry with `AdvancedAdaptiveTrader.mq5` / `trice.mq5`
   via MT5's `Common/Files/nolo_bridge/` shared memory / file pipe.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from nolo.types import RegimeState, Signal


class MT5RealTimeBridge:
    """Bi-directional real-time bridge between Python Quant Engine and MetaTrader 5 EA."""

    def __init__(self, bridge_dir: Optional[Path] = None) -> None:
        self.bridge_dir = bridge_dir or Path("/volumes/macx/projects/nolobo/.mt5_bridge")
        self.bridge_dir.mkdir(parents=True, exist_ok=True)
