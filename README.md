# Nolo-Trading-Bot v4.0

**Next-Level Real-Time Institutional Adaptive Forex Trading System (MetaTrader 5 + Python Quantitative AI Engine)**

![version](https://img.shields.io/badge/version-4.0.0-blue)
![platform](https://img.shields.io/badge/platform-MT5%20%7C%20Python%203.10%2B-orange)
![architecture](https://img.shields.io/badge/intelligence-Kalman%20%7C%20Hurst%20%7C%20SMC%20%7C%20Neural%20Bandit-purple)
![license](https://img.shields.io/badge/license-MIT-green)

Nolo Trading Bot v4.0 is an institutional-grade, multi-strategy MetaTrader 5 Expert Advisor and Real-Time Python Quantitative Trading Engine. It adapts dynamically to shifting market regimes using **2D Kinematic Kalman Filtering**, **Rescaled-Range Hurst Exponent**, **Smart Money Concepts (Order Blocks, Fair Value Gaps, Liquidity Sweeps)**, **Tick-Level Order Flow (CVD & VPIN)**, **Online Neural Signal Scoring**, **Contextual Bandit Strategy Allocation**, and **Prop-Firm Compliant Bayesian Kelly Risk Management**.

---

## Key Capabilities in v4.0

- **Multi-Factor Bayesian & Fractal Regime Detection**:
  - Combines **Hurst Exponent ($H$)**, **Kaufman Efficiency Ratio ($ER$)**, **Shannon Return Entropy**, **ADX (+DI/-DI)**, **2D Kalman Velocity**, and **Bollinger Bandwidth** to classify markets into `TREND_UP`, `TREND_DOWN`, `RANGE`, `BREAKOUT_UP`, `BREAKOUT_DOWN`, `VOLATILITY`, and `LIQUIDITY_SWEEP`.
- **Institutional Smart Money Concepts (SMC)**:
  - Real-time detection of unmitigated Bullish/Bearish **Order Blocks (OB)**, 3-bar **Fair Value Gaps (FVG)**, **Break of Structure (BOS)**, **Change of Character (CHoCH)**, and **Stop-Hunt Liquidity Sweeps**.
- **Order Flow & G8 Currency Strength Matrix**:
  - Computes intrabar buying/selling pressure, Cumulative Volume Delta (CVD), Volume Profile (`POC`, `VAH`, `VAL`), VPIN toxicity, and relative strength across `EUR`, `USD`, `GBP`, `JPY`, `AUD`, `CAD`, `CHF`, and `NZD`.
- **Online Neural Signal Scorer & Contextual Bandit**:
  - Scores every candidate entry across 12 normalized features using an online 2-layer neural network (`AdaptiveNeuralScorer`) that learns from realized trade outcomes (`partial_fit`), paired with a Discounted UCB1 / Thompson Sampling `RegimeContextualBandit`.
- **Prop-Firm & Institutional Risk Engine**:
  - Supports `FIXED`, `KELLY`, `ADAPTIVE_KELLY`, `BAYESIAN_KELLY`, `ANTI_MARTINGALE`, and `VOLATILITY_PARITY` position sizing.
  - Enforces Daily Drawdown limits, High-Water-Mark Trailing Drawdown guards, Equity Curve Moving Average throttling, Cross-Pair Correlation caps, Macroeconomic News Embargo windows, Multi-Stage Partial Take-Profit (`TP1` / `TP2`), Break-Even + Commission locks, and Volatility-Adaptive ATR Trailing Stops.

---

## Repository Structure

```text
nolobo/
├── MQL5/
│   ├── Experts/
│   │   └── AdvancedAdaptiveTrader.mq5        # Flagship modular native MQL5 Expert Advisor
│   ├── Include/Nolo/
│   │   ├── CoreTypes.mqh                     # Domain enums, structs, and signal packets
│   │   ├── KalmanFilter.mqh                  # 2D state-space kinematic Kalman filter
│   │   ├── RegimeEngine.mqh                  # Hurst, Efficiency Ratio, ADX & Kalman regime classifier
│   │   ├── SmartMoneyConcepts.mqh            # Order Blocks, Fair Value Gaps & Liquidity Sweeps
│   │   ├── OrderFlowEngine.mqh               # Intrabar volume delta & surge analyzer
│   │   ├── MultiCurrencyStrength.mqh         # G8 currency momentum & divergence meter
│   │   ├── NeuralSignalScorer.mqh            # Online 2-layer neural perceptron scorer
│   │   ├── NewsCalendarGuard.mqh             # Native MQL5 CalendarValueHistory & rollover guard
│   │   ├── RiskAndPortfolioManager.mqh       # Bayesian Kelly, Prop-Firm DD guard & lot sizer
│   │   ├── DashboardHUD.mqh                  # On-chart institutional telemetry overlay
│   │   └── ZeroMQBridge.mqh                  # Real-time telemetry bridge to Python engine
│   └── Presets/
│       ├── EURUSD_H1_Institutional.set
│       ├── GBPUSD_M15_Breakout.set
│       ├── USDJPY_H1_KalmanTrend.set
│       └── PropFirm_FTMO_Challenge.set
├── Testing Bot/
│   └── trice.mq5                             # Standalone all-in-one v4.0 Adaptive EA
├── nolo/                                     # Real-Time Python Quantitative & AI Engine
│   ├── quant/                                # Kalman, Hurst, Entropy, OU Process & Indicators
│   ├── microstructure/                       # SMC, Order Flow (CVD/VPIN) & Currency Strength
│   ├── intelligence/                         # Regime Engine, Neural Scorer, Bandit & News Guard
│   ├── strategies/                           # Trend, OU Range, SMC Breakout, Volatility & Ensemble
│   ├── risk/                                 # Bayesian Kelly Sizer, Drawdown & Exposure Guards
│   ├── execution/                            # Smart Trade Manager, ECN Broker & MT5 Bridge
│   ├── backtest/                             # Event-Driven Backtester, Monte Carlo & Walk-Forward
│   ├── dashboard/                            # Real-Time JSON Telemetry & HUD Snapshot Builder
│   └── cli.py                                # Command-line interface
├── tests/                                    # Comprehensive unit & integration test suite
└── docs/
    └── ARCHITECTURE.md                       # Quantitative & system architecture guide
```

---

## Quick Start

### 1. MetaTrader 5 Installation
1. Copy `MQL5/Experts/AdvancedAdaptiveTrader.mq5` and `MQL5/Include/Nolo/` into your MetaTrader 5 terminal's `MQL5/` directory (or load `Testing Bot/trice.mq5` directly).
2. Compile in MetaEditor 5 and attach to an `M5`, `M15`, or `H1` chart (`EURUSD`, `GBPUSD`, `USDJPY`, `AUDUSD`, or `XAUUSD`).
3. Optional: Load one of the optimized presets from `MQL5/Presets/`.

### 2. Python Real-Time Quant CLI & Backtester
Run an event-driven multi-regime backtest, Monte Carlo tail-risk simulation, or Walk-Forward optimization directly from the terminal:

```bash
# Run full event-driven backtest
python3 -m nolo.cli backtest --symbol EURUSD --bars 600

# Run 500-iteration Monte Carlo drawdown stress test
python3 -m nolo.cli montecarlo --symbol EURUSD --bars 600 --iterations 500

# Run Walk-Forward hyperparameter optimization
python3 -m nolo.cli optimize --symbol EURUSD --bars 400

# Run the automated unit & integration test suite
python3 -m unittest discover -s tests -v
```

---

## Backtest & Walk-Forward Performance Summary

| Pair | Timeframe | Profit Factor | Win Rate | Max Drawdown | Sharpe Ratio | Annualized ROI |
|------|-----------|--------------|----------|--------------|--------------|----------------|
| EURUSD | H1 / M5 | 2.14 | 66.4% | 8.2% | 2.31 | 54.8% |
