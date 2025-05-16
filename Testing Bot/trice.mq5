//+------------------------------------------------------------------+
//| Advanced Adaptive Trading Bot - Multi-Strategy System v4.0       |
//| Combines machine learning prediction, Kalman state estimation,   |
//| Hurst regime detection, Smart Money Concepts, and Bayesian Kelly |
//+------------------------------------------------------------------+
#property strict
#property copyright   "Market Expert 2025 - Nolo Quantitative Systems"
#property link        "https://github.com/festomanolo/Nolo-Trading-Bot"
#property version     "4.0"
#property description "Next-Level Multi-Timeframe Adaptive Forex Trading Strategy with Kalman Filter, Hurst Exponent, Smart Money Concepts & Online Neural Scorer"

// Enumerations for strategy flexibility
enum REGIME_TYPE 
{
   TREND_FOLLOWING,    // Trend Following Mode (Kalman + SuperTrend + Ichimoku)
   RANGE_TRADING,      // Range / Ornstein-Uhlenbeck Mean Reversion Mode
