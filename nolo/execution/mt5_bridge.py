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

