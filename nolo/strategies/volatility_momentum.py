"""
TTM Volatility Squeeze & Order Flow Momentum Expansion Strategy.

Designed for explosive volatility regimes:
- Detects Bollinger-inside-Keltner Volatility Squeeze release or ATR expansion (>1.25x)
- Confirms momentum acceleration via Fast EMA slope, RSI surge, and Order Flow CVD delta
- Uses tighter dynamic stop-loss (1.5x ATR) to protect capital during high volatility
"""
