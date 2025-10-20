"""
Prop-Firm Compliant Daily & Trailing Drawdown Guard + Equity Curve Filter.

Enforces:
1. Daily Balance & Equity Drawdown Limit (resets each trading day)
2. Maximum Overall Trailing Drawdown from High-Water Mark (FTMO / Prop-Firm protection)
3. Daily Trade Count Cap & Minimum Bars Since Last Trade
4. Equity Curve Moving Average Throttle (scales risk down by 50% when equity < SMA(equity))
