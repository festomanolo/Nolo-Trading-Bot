"""
Real-Time Event-Driven Trading Engine.

Orchestrates the complete lifecycle on every bar/tick:
1. Spread & Liquidity Shock Guard
2. Prop-Firm Daily & Total Trailing Drawdown Check
3. Open Trade Management (Break-Even, TP1/TP2 Partial Close, Smart ATR Trailing Stop)
4. Macroeconomic News Embargo Filter
