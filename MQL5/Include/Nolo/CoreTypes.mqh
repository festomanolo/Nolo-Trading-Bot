//+------------------------------------------------------------------+
//|                                                    CoreTypes.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|                                   https://github.com/festomanolo |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property link      "https://github.com/festomanolo/Nolo-Trading-Bot"
#property strict

#ifndef NOLO_CORE_TYPES_MQH
#define NOLO_CORE_TYPES_MQH

enum REGIME_TYPE
{
   TREND_FOLLOWING,    // Trend Following Mode
   RANGE_TRADING,      // Range / Ornstein-Uhlenbeck Mean Reversion Mode
   BREAKOUT,           // Institutional Breakout & SMC Mode
   VOLATILITY,         // Volatility Squeeze & Momentum Mode
   SMC_INSTITUTIONAL,  // Pure Smart Money Concepts (OB/FVG/Sweep)
   ADAPTIVE            // Auto-detect Regime via Bayesian + Hurst + Kalman
};

enum RISK_MODEL
{
   FIXED,              // Fixed Risk %
   KELLY,              // Classic Kelly Criterion
   ADAPTIVE_KELLY,     // Streak-Adjusted Adaptive Kelly
   BAYESIAN_KELLY,     // Bayesian Beta-Posterior + Neural Probability Kelly
   ANTI_MARTINGALE,    // Geometric Win-Streak Scaling
   VOLATILITY_PARITY   // Inverse ATR Volatility Risk Parity
};

enum SMC_BIAS_TYPE
