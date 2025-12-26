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
