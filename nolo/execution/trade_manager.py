"""
Smart Exit & Open Trade Lifecycle Manager.

Implements:
1. Break-Even + Commission Buffer Stop Modification
2. Multi-Stage Partial Take-Profit (TP1 at 1.0R, TP2 at 1.8R)
3. Volatility-Adaptive ATR Trailing Stop (tightens smoothly as profit grows)
"""
