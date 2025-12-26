# Nolo Trading Bot v4.0 — Institutional Quantitative Architecture

## 1. System Overview

Nolo Trading Bot v4.0 combines a **Native MetaTrader 5 Expert Advisor Suite (`MQL5/` & `Testing Bot/`)** with a **Real-Time Python Quantitative & AI Engine (`nolo/`)**.

```mermaid
flowchart TD
    A["Live Market Stream (MT5 Tick/Bar Feed)"] --> B["State-Space & Fractal Feature Engine"]
    B --> B1["2D Kinematic Kalman Filter (Level & Velocity)"]
    B --> B2["Rescaled Range Hurst Exponent & Fractal Dimension"]
    B --> B3["Shannon Return Entropy & Kaufman Efficiency Ratio"]
    B --> C["Microstructure & Smart Money Concepts (SMC)"]
    C --> C1["Order Blocks (OB) & Fair Value Gaps (FVG)"]
    C --> C2["Liquidity Sweep / Stop-Hunt Detector"]
    C --> C3["Tick Order Flow Delta, CVD & VPIN Toxicity"]
    C --> C4["G8 Multi-Currency Strength & Correlation Matrix"]
    B1 & B2 & B3 & C --> D["Bayesian & Markov Regime Classifier"]
    D --> E["Multi-Strategy Alpha Suite"]
    E --> E1["Kalman + SuperTrend + Ichimoku Trend"]
    E --> E2["Ornstein-Uhlenbeck Mean Reversion"]
    E --> E3["SMC Liquidity Sweep & Volume Breakout"]
    E --> E4["TTM Volatility Squeeze & Momentum"]
    E1 & E2 & E3 & E4 --> F["Online Neural Signal Scorer & Contextual Bandit"]
    F --> G["Prop-Firm Risk & Portfolio Manager"]
    G --> H["Execution & Smart Trade Lifecycle (BE, TP1/TP2, Smart Trail)"]
```

## 2. Core Quantitative Pillars

1. **State-Space Kalman Filter (`nolo/quant/kalman.py` & `MQL5/Include/Nolo/KalmanFilter.mqh`)**:
   - Models latent price level and trend velocity with dynamic innovation covariance scaling.
