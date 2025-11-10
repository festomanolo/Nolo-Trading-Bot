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
        self._mt5_module: Any = None
        self._connected: bool = False

    def try_connect_native_mt5(self) -> bool:
        """Attempt to initialize native MetaTrader5 Python binding if installed."""
        try:
            import MetaTrader5 as mt5  # type: ignore

            if mt5.initialize():
                self._mt5_module = mt5
                self._connected = True
                return True
        except Exception:
            self._connected = False
        return False

    def publish_signal_and_regime(
        self,
        symbol: str,
        regime_state: RegimeState,
        signal: Optional[Signal] = None,
    ) -> Path:
        """
        Write atomic real-time telemetry packet consumed by `ZeroMQBridge.mqh` in MT5.
        """
        payload: Dict[str, Any] = {
            "symbol": symbol,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "regime": {
                "name": regime_state.regime.value,
                "confidence": round(regime_state.confidence, 4),
                "hurst": round(regime_state.hurst_exponent, 4),
                "efficiency_ratio": round(regime_state.efficiency_ratio, 4),
