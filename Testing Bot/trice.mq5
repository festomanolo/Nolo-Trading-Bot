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
   BREAKOUT,           // Institutional Breakout & SMC Mode
   VOLATILITY,         // Volatility Squeeze & Momentum Mode
   SMC_INSTITUTIONAL,  // Smart Money Concepts (Order Block / FVG / Sweep)
   ADAPTIVE            // Auto-detect Regime (Bayesian + Hurst + ADX + Kalman)
};

enum RISK_MODEL 
{
   FIXED,              // Fixed Risk %
   KELLY,              // Classic Kelly Criterion
   ADAPTIVE_KELLY,     // Streak-Adjusted Adaptive Kelly
   BAYESIAN_KELLY,     // Bayesian Beta-Posterior + Neural Probability Kelly
   ANTI_MARTINGALE     // Anti-Martingale (increase size after wins)
};

// Input Parameters - Strategy Selection & Intelligence
input REGIME_TYPE MarketRegimeMode           = ADAPTIVE;        // Market Regime Detection Method
input RISK_MODEL  RiskModelType              = BAYESIAN_KELLY;  // Risk Management Method
input bool        UseVolatilityFilter        = true;            // Filter trades during extreme volatility
input bool        UsePriceMomentum           = true;            // Use Kalman & OrderFlow momentum confirmation
input bool        UseMarketStructure         = true;            // Use SMC market structure (S/R, OB, FVG)
input bool        UseAlternateTimeframes     = true;            // Use multi-timeframe confirmation
input bool        UseSmartTrailingStop       = true;            // Enable volatility-adaptive trailing stop
input bool        UseNeuralSignalFilter      = true;            // Enable Online Neural Perceptron Scorer
input bool        UseMacroNewsFilter         = true;            // Enable High-Impact News & Rollover Guard
input bool        ShowTelemetryHUD           = true;            // Show On-Chart Institutional Telemetry HUD

// Input Parameters - Moving Averages
input ENUM_TIMEFRAMES MainTimeframe          = PERIOD_M5;       // Main trading timeframe
input ENUM_TIMEFRAMES HigherTimeframe        = PERIOD_H1;       // Higher confirmation timeframe
input int         FastMAPeriod               = 8;               // Fast MA period (optimized)
input int         SlowMAPeriod               = 21;              // Slow MA period
input ENUM_MA_METHOD FastMAMethod            = MODE_EMA;        // Fast MA method
input ENUM_MA_METHOD SlowMAMethod            = MODE_EMA;        // Slow MA method

// Input Parameters - Oscillators
input int         RSIPeriod                  = 14;              // RSI period
input int         RSI_UpperLevel             = 70;              // RSI upper threshold
input int         RSI_LowerLevel             = 30;              // RSI lower threshold
input int         StochasticKPeriod          = 5;               // Stochastic %K period
input int         StochasticDPeriod          = 3;               // Stochastic %D period
input int         StochasticSlowing          = 3;               // Stochastic slowing

// Input Parameters - MACD
input int         MACD_FastEMA               = 12;              // MACD Fast EMA
input int         MACD_SlowEMA               = 26;              // MACD Slow EMA
input int         MACD_SignalSMA             = 9;               // MACD Signal SMA

// Input Parameters - Bollinger & ATR
input int         BollingerPeriod            = 20;              // Bollinger Bands period
input double      BollingerDeviation         = 2.0;             // Bollinger Bands deviation
input int         ATRPeriod                  = 14;              // ATR period for volatility

// Input Parameters - SuperTrend & Ichimoku
input double      SuperTrendMultiplier       = 2.5;             // SuperTrend multiplier (optimized)
input int         TenkanSen                  = 9;               // Ichimoku Tenkan-sen period
input int         KijunSen                   = 26;              // Ichimoku Kijun-sen period
input int         SenkouSpanB                = 52;              // Ichimoku Senkou Span B period

// Input Parameters - Advanced Risk Management
input double      MaxRisk                    = 1.0;             // Maximum risk per trade (%)
input double      AdaptiveRiskMultiplier     = 1.4;             // Risk multiplier for strong signals
input double      ATRMultiplier              = 2.0;             // ATR multiplier for stop loss
input double      Slippage                   = 3.0;             // Maximum slippage allowed
input int         MaxDrawdown                = 5;               // Max daily drawdown %
