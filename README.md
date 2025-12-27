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
