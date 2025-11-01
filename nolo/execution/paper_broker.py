"""
Realistic ECN Paper & Backtest Broker Engine.

Models:
- Bid/Ask spread execution (BUY at Ask, SELL at Bid)
- Slippage modeling proportional to order size and volatility
- ECN round-turn commission per lot
- Partial position closes, SL/TP triggers, and real-time mark-to-market equity
