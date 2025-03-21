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
{
   BIAS_NEUTRAL = 0,
   BIAS_BULLISH_BOS = 1,
   BIAS_BEARISH_BOS = -1,
   BIAS_BULLISH_CHOCH = 2,
   BIAS_BEARISH_CHOCH = -2
};

struct NoloRegimeSnapshot
{
   string        regimeName;
   double        confidence;
   double        hurstExponent;
   double        efficiencyRatio;
   double        adxValue;
   double        plusDI;
   double        minusDI;
   double        bbWidthPct;
   double        atrRatio;
   double        kalmanVelocity;
   double        shannonEntropy;
   SMC_BIAS_TYPE structureBias;
};

struct NoloSMCZone
{
   int      zoneType;      // 1=Bull OB, -1=Bear OB, 2=Bull FVG, -2=Bear FVG
   double   topPrice;
   double   bottomPrice;
   datetime createdTime;
   int      barIndex;
   bool     mitigated;
   double   strength;
