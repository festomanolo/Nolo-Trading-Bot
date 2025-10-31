"""
Smart Exit & Open Trade Lifecycle Manager.

Implements:
1. Break-Even + Commission Buffer Stop Modification
2. Multi-Stage Partial Take-Profit (TP1 at 1.0R, TP2 at 1.8R)
3. Volatility-Adaptive ATR Trailing Stop (tightens smoothly as profit grows)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from nolo.config import BotConfig
from nolo.types import OrderSide, Position


@dataclass
class TradeAction:
    """Instruction produced by SmartTradeManager for an open position."""

    ticket: int
    action_type: str  # "MODIFY_SL", "PARTIAL_CLOSE", "FULL_CLOSE"
    new_sl: Optional[float] = None
    close_lots: float = 0.0
    reason: str = ""


class SmartTradeManager:
    """Evaluates open positions on every tick/bar for break-even, partial TP, and adaptive trailing stops."""

    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.config = config or BotConfig()

    def manage_position(
        self,
        pos: Position,
        bid: float,
        ask: float,
        current_atr: float,
        reference_atr: float,
    ) -> List[TradeAction]:
        """Inspect a single open position and return any required modification/close actions."""
        actions: List[TradeAction] = []
        spec = self.config.get_symbol_spec(pos.symbol)
        rcfg = self.config.risk

        mark_price = bid if pos.side == OrderSide.BUY else ask
        pos.current_price = mark_price
        if pos.side == OrderSide.BUY:
            pos.highest_favorable_price = max(pos.highest_favorable_price, mark_price)
        else:
            pos.lowest_favorable_price = min(pos.lowest_favorable_price, mark_price)

        pips_profit = pos.unrealized_pips(spec.pip_size)
        initial_risk_price = max(spec.pip_size * 5.0, abs(pos.open_price - pos.initial_stop_loss))
        current_r = (
            (mark_price - pos.open_price) / initial_risk_price
            if pos.side == OrderSide.BUY
            else (pos.open_price - mark_price) / initial_risk_price
        )

        # 1. Partial Take-Profit Scaling (TP1 & TP2)
        if rcfg.use_partial_tp and pos.current_lots >= spec.min_lot * 2:
            if not pos.tp1_hit and current_r >= rcfg.tp1_r_multiple:
                close_qty = round(
                    max(spec.min_lot, round((pos.initial_lots * rcfg.tp1_close_fraction) / spec.lot_step) * spec.lot_step),
                    2,
                )
                if close_qty < pos.current_lots:
                    pos.tp1_hit = True
                    actions.append(
                        TradeAction(
                            ticket=pos.ticket,
                            action_type="PARTIAL_CLOSE",
                            close_lots=close_qty,
                            reason=f"TP1 reached ({current_r:.2f}R >= {rcfg.tp1_r_multiple:.2f}R)",
                        )
                    )

            elif pos.tp1_hit and not pos.tp2_hit and current_r >= rcfg.tp2_r_multiple:
                close_qty = round(
                    max(spec.min_lot, round((pos.initial_lots * rcfg.tp2_close_fraction) / spec.lot_step) * spec.lot_step),
                    2,
                )
                if close_qty < pos.current_lots:
                    pos.tp2_hit = True
                    actions.append(
                        TradeAction(
                            ticket=pos.ticket,
                            action_type="PARTIAL_CLOSE",
                            close_lots=close_qty,
                            reason=f"TP2 reached ({current_r:.2f}R >= {rcfg.tp2_r_multiple:.2f}R)",
                        )
                    )

        # 2. Break-Even Stop Lock (triggered once 1.0R / TP1 is reached so normal pullbacks don't clip early)
        if rcfg.use_breakeven and (current_r >= 1.0 or pips_profit >= rcfg.breakeven_trigger_pips * 1.4):
            if pos.side == OrderSide.BUY:
                be_sl = round(pos.open_price + rcfg.breakeven_plus_pips * spec.pip_size, spec.digits)
                if pos.stop_loss == 0.0 or pos.stop_loss < pos.open_price:
                    pos.breakeven_applied = True
                    actions.append(
                        TradeAction(
                            ticket=pos.ticket,
                            action_type="MODIFY_SL",
                            new_sl=be_sl,
                            reason=f"Break-even lock (+{rcfg.breakeven_plus_pips} pips)",
                        )
                    )
            else:
                be_sl = round(pos.open_price - rcfg.breakeven_plus_pips * spec.pip_size, spec.digits)
                if pos.stop_loss == 0.0 or pos.stop_loss > pos.open_price:
                    pos.breakeven_applied = True
                    actions.append(
                        TradeAction(
                            ticket=pos.ticket,
                            action_type="MODIFY_SL",
                            new_sl=be_sl,
                            reason=f"Break-even lock (+{rcfg.breakeven_plus_pips} pips)",
                        )
                    )

        # 3. Volatility-Adaptive Smart Trailing Stop
        if rcfg.use_smart_trailing and pips_profit >= rcfg.trailing_activation_pips:
            atr_scale = 1.0
            if reference_atr > 1e-9 and current_atr > 0:
                atr_scale = max(0.65, min(1.50, current_atr / reference_atr))
            adaptive_trail_pips = rcfg.trailing_distance_pips * atr_scale
            trail_dist_price = adaptive_trail_pips * spec.pip_size
