"""
Institutional Smart Money Concepts (SMC) & Price Action Microstructure Engine.

Detects:
1. Fractal Swing Highs & Swing Lows
2. Break of Structure (BOS) & Change of Character (CHoCH)
3. Bullish & Bearish Order Blocks (OB) with impulse validation and mitigation tracking
4. Bullish & Bearish Fair Value Gaps (FVG / 3-bar imbalances)
5. Buy-Side & Sell-Side Liquidity Sweeps (Stop Hunts / Turtle Soup reversals)
6. Dealing Range Premium / Equilibrium / Discount positioning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from nolo.config import SMCConfig
from nolo.quant.indicators import IndicatorEngine
from nolo.types import Bar, MarketStructureBias, SMCZone, SMCZoneType


@dataclass
class SMCSnapshot:
    """Complete institutional structure snapshot at the current bar."""

    structure_bias: MarketStructureBias
    last_swing_high: float
    last_swing_low: float
    dealing_range_position: float  # 0.0 = extreme discount, 0.5 = equilibrium, 1.0 = extreme premium
    in_bullish_ob: bool
    in_bearish_ob: bool
    in_bullish_fvg: bool
    in_bearish_fvg: bool
    bullish_liquidity_sweep: bool
    bearish_liquidity_sweep: bool
    active_zones: List[SMCZone] = field(default_factory=list)
    nearest_support: float = 0.0
    nearest_resistance: float = 0.0


class SmartMoneyAnalyzer:
    """Analyzes OHLCV bars for institutional Smart Money footprints."""

    def __init__(self, config: Optional[SMCConfig] = None) -> None:
        self.config = config or SMCConfig()

    def analyze(self, bars: Sequence[Bar]) -> SMCSnapshot:
        n = len(bars)
        if n < 15:
            last_p = bars[-1].close if n > 0 else 0.0
            return SMCSnapshot(
                structure_bias=MarketStructureBias.NEUTRAL,
                last_swing_high=last_p,
                last_swing_low=last_p,
                dealing_range_position=0.5,
                in_bullish_ob=False,
                in_bearish_ob=False,
                in_bullish_fvg=False,
                in_bearish_fvg=False,
                bullish_liquidity_sweep=False,
                bearish_liquidity_sweep=False,
                nearest_support=last_p,
                nearest_resistance=last_p,
            )

        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        atr_vals = IndicatorEngine.atr(highs, lows, closes, 14)

        swing_highs, swing_lows = self._find_swing_points(bars)
        last_sh = swing_highs[-1][1] if swing_highs else max(highs[-20:])
        last_sl = swing_lows[-1][1] if swing_lows else min(lows[-20:])

        prev_sh = swing_highs[-2][1] if len(swing_highs) >= 2 else last_sh
        prev_sl = swing_lows[-2][1] if len(swing_lows) >= 2 else last_sl

        curr_close = closes[-1]
        structure_bias = self._classify_structure(curr_close, last_sh, prev_sh, last_sl, prev_sl)

        # Dealing range (50-bar institutional range)
        range_high = max(highs[-min(n, 50) :])
        range_low = min(lows[-min(n, 50) :])
        span = max(1e-9, range_high - range_low)
        dealing_pos = max(0.0, min(1.0, (curr_close - range_low) / span))

        zones = self._detect_zones(bars, atr_vals)

        in_bull_ob = any(
            z.zone_type == SMCZoneType.BULLISH_OB and not z.mitigated and z.contains(curr_close)
            for z in zones
        )
        in_bear_ob = any(
            z.zone_type == SMCZoneType.BEARISH_OB and not z.mitigated and z.contains(curr_close)
            for z in zones
        )
        in_bull_fvg = any(
            z.zone_type == SMCZoneType.BULLISH_FVG and not z.mitigated and z.contains(curr_close)
            for z in zones
        )
        in_bear_fvg = any(
            z.zone_type == SMCZoneType.BEARISH_FVG and not z.mitigated and z.contains(curr_close)
            for z in zones
        )

        bull_sweep, bear_sweep = self._detect_liquidity_sweep(bars, last_sh, last_sl)

        supports = [z.bottom for z in zones if z.midpoint <= curr_close and not z.mitigated]
        resistances = [z.top for z in zones if z.midpoint >= curr_close and not z.mitigated]

        nearest_sup = max(supports) if supports else min(lows[-20:])
        nearest_res = min(resistances) if resistances else max(highs[-20:])

        return SMCSnapshot(
            structure_bias=structure_bias,
            last_swing_high=last_sh,
            last_swing_low=last_sl,
            dealing_range_position=dealing_pos,
            in_bullish_ob=in_bull_ob,
            in_bearish_ob=in_bear_ob,
            in_bullish_fvg=in_bull_fvg,
            in_bearish_fvg=in_bear_fvg,
            bullish_liquidity_sweep=bull_sweep,
            bearish_liquidity_sweep=bear_sweep,
            active_zones=zones[-self.config.max_active_zones :],
            nearest_support=nearest_sup,
            nearest_resistance=nearest_res,
        )

    def _find_swing_points(
        self, bars: Sequence[Bar]
    ) -> tuple[List[tuple[int, float]], List[tuple[int, float]]]:
        w = max(2, self.config.swing_length)
        n = len(bars)
        swing_highs: List[tuple[int, float]] = []
        swing_lows: List[tuple[int, float]] = []

        for i in range(w, n - w):
            h = bars[i].high
            l = bars[i].low
            is_sh = all(h >= bars[j].high for j in range(i - w, i + w + 1) if j != i)
            is_sl = all(l <= bars[j].low for j in range(i - w, i + w + 1) if j != i)
            if is_sh:
                swing_highs.append((i, h))
            if is_sl:
                swing_lows.append((i, l))
        return swing_highs, swing_lows

    @staticmethod
    def _classify_structure(
        curr_close: float,
        last_sh: float,
        prev_sh: float,
        last_sl: float,
        prev_sl: float,
    ) -> MarketStructureBias:
        if curr_close > last_sh:
            if last_sl < prev_sl:
                return MarketStructureBias.BULLISH_CHOCH
            return MarketStructureBias.BULLISH_BOS
        if curr_close < last_sl:
            if last_sh > prev_sh:
                return MarketStructureBias.BEARISH_CHOCH
            return MarketStructureBias.BEARISH_BOS
        if last_sh > prev_sh and last_sl >= prev_sl:
            return MarketStructureBias.BULLISH_BOS
        if last_sh <= prev_sh and last_sl < prev_sl:
            return MarketStructureBias.BEARISH_BOS
        return MarketStructureBias.NEUTRAL

    def _detect_zones(self, bars: Sequence[Bar], atr_vals: Sequence[float]) -> List[SMCZone]:
        n = len(bars)
        start = max(2, n - 80)
        zones: List[SMCZone] = []

        for i in range(start, n):
            atr = max(1e-9, atr_vals[i])
            b_prev2 = bars[i - 2]
            b_prev1 = bars[i - 1]
            b_curr = bars[i]

            # 1. Bullish Fair Value Gap (b_curr.low > b_prev2.high with strong middle impulse)
            gap_up = b_curr.low - b_prev2.high
            if gap_up >= atr * self.config.fvg_min_atr_fraction and b_prev1.is_bullish:
                zones.append(
                    SMCZone(
                        zone_type=SMCZoneType.BULLISH_FVG,
                        top=b_curr.low,
                        bottom=b_prev2.high,
                        created_at=b_curr.timestamp,
                        bar_index=i,
                        strength=min(3.0, gap_up / atr),
                    )
                )
                # Corresponding Bullish Order Block (last bearish candle prior to impulse)
                if not b_prev2.is_bullish:
                    zones.append(
                        SMCZone(
                            zone_type=SMCZoneType.BULLISH_OB,
                            top=max(b_prev2.open, b_prev2.close),
                            bottom=b_prev2.low,
                            created_at=b_prev2.timestamp,
                            bar_index=i - 2,
                            strength=min(3.0, b_prev1.body / atr),
                        )
                    )

            # 2. Bearish Fair Value Gap (b_prev2.low > b_curr.high with strong middle impulse)
            gap_down = b_prev2.low - b_curr.high
            if gap_down >= atr * self.config.fvg_min_atr_fraction and not b_prev1.is_bullish:
                zones.append(
                    SMCZone(
                        zone_type=SMCZoneType.BEARISH_FVG,
                        top=b_prev2.low,
                        bottom=b_curr.high,
                        created_at=b_curr.timestamp,
                        bar_index=i,
                        strength=min(3.0, gap_down / atr),
                    )
                )
                if b_prev2.is_bullish:
                    zones.append(
                        SMCZone(
                            zone_type=SMCZoneType.BEARISH_OB,
                            top=b_prev2.high,
                            bottom=min(b_prev2.open, b_prev2.close),
                            created_at=b_prev2.timestamp,
                            bar_index=i - 2,
                            strength=min(3.0, b_prev1.body / atr),
                        )
                    )

            # Update mitigation status of earlier zones
            for z in zones:
                if z.bar_index >= i - 1 or z.mitigated:
                    continue
                if z.zone_type in (SMCZoneType.BULLISH_OB, SMCZoneType.BULLISH_FVG):
                    if b_curr.low <= z.top:
                        z.touch_count += 1
                    if b_curr.close < z.bottom:
                        z.mitigated = True
                elif z.zone_type in (SMCZoneType.BEARISH_OB, SMCZoneType.BEARISH_FVG):
                    if b_curr.high >= z.bottom:
