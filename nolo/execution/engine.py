"""
Real-Time Event-Driven Trading Engine.

Orchestrates the complete lifecycle on every bar/tick:
1. Spread & Liquidity Shock Guard
2. Prop-Firm Daily & Total Trailing Drawdown Check
3. Open Trade Management (Break-Even, TP1/TP2 Partial Close, Smart ATR Trailing Stop)
4. Macroeconomic News Embargo Filter
5. Ensemble Signal Generation (Regime + SMC + OrderFlow + Neural Scorer + Bandit)
6. Currency Exposure & Correlation Guard
7. Bayesian Kelly Position Sizing & Order Execution
8. Online ML Feedback Loop on Trade Closure
"""

from __future__ import annotations

