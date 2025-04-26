//+------------------------------------------------------------------+
//|                                       AdvancedAdaptiveTrader.mq5 |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|    Multi-Strategy Real-Time Adaptive Forex Expert Advisor (MT5)  |
//+------------------------------------------------------------------+
#property copyright   "Nolo Quantitative Systems 2025"
#property link        "https://github.com/festomanolo/Nolo-Trading-Bot"
#property version     "4.00"
#property description "Institutional Adaptive Forex EA: Kalman Filter, Hurst Exponent, SMC (OB/FVG/Sweep), Order Flow, Online Neural Scorer & Prop-Firm Risk Engine"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <Trade\AccountInfo.mqh>

#include "..\Include\Nolo\CoreTypes.mqh"
#include "..\Include\Nolo\KalmanFilter.mqh"
#include "..\Include\Nolo\RegimeEngine.mqh"
#include "..\Include\Nolo\SmartMoneyConcepts.mqh"
#include "..\Include\Nolo\OrderFlowEngine.mqh"
#include "..\Include\Nolo\MultiCurrencyStrength.mqh"
#include "..\Include\Nolo\NeuralSignalScorer.mqh"
#include "..\Include\Nolo\NewsCalendarGuard.mqh"
#include "..\Include\Nolo\RiskAndPortfolioManager.mqh"
#include "..\Include\Nolo\DashboardHUD.mqh"
#include "..\Include\Nolo\ZeroMQBridge.mqh"

//--- Input Parameters: Strategy & Intelligence
input REGIME_TYPE     MarketRegimeMode           = ADAPTIVE;       // Market Regime Detection Mode
input RISK_MODEL      RiskModelType              = BAYESIAN_KELLY; // Institutional Risk Sizing Model
input bool            UseVolatilityFilter        = true;           // Filter entries during extreme chop
input bool            UsePriceMomentum           = true;           // Confirm with Kalman & OrderFlow momentum
input bool            UseMarketStructure         = true;           // Use SMC Swing/OB/FVG structure stops
input bool            UseAlternateTimeframes     = true;           // Multi-timeframe (HTF) confirmation
input bool            UseSmartTrailingStop       = true;           // Volatility-adaptive ATR trailing stop
input bool            UseNeuralScorer            = true;           // Online Neural Perceptron signal filter
input bool            UseNewsCalendarGuard       = true;           // High-impact macro news & rollover guard
input bool            ShowDashboardHUD           = true;           // Render real-time on-chart telemetry HUD
input bool            EnablePythonBridge         = false;          // Publish telemetry to Python Quant Engine

//--- Input Parameters: Timeframes & Moving Averages
input ENUM_TIMEFRAMES MainTimeframe              = PERIOD_M5;      // Main trading timeframe
input ENUM_TIMEFRAMES HigherTimeframe            = PERIOD_H1;      // Higher confirmation timeframe
input int             FastMAPeriod               = 8;              // Fast EMA period
input int             SlowMAPeriod               = 21;             // Slow EMA period
input ENUM_MA_METHOD  FastMAMethod               = MODE_EMA;       // Fast MA method
input ENUM_MA_METHOD  SlowMAMethod               = MODE_EMA;       // Slow MA method

//--- Input Parameters: Oscillators & MACD
input int             RSIPeriod                  = 14;             // RSI period
input int             RSI_UpperLevel             = 70;             // RSI upper threshold
input int             RSI_LowerLevel             = 30;             // RSI lower threshold
input int             StochasticKPeriod          = 5;              // Stochastic %K period
input int             StochasticDPeriod          = 3;              // Stochastic %D period
input int             StochasticSlowing          = 3;              // Stochastic slowing
input int             MACD_FastEMA               = 12;             // MACD Fast EMA
input int             MACD_SlowEMA               = 26;             // MACD Slow EMA
input int             MACD_SignalSMA             = 9;              // MACD Signal SMA

//--- Input Parameters: Volatility, SuperTrend & Ichimoku
input int             BollingerPeriod            = 20;             // Bollinger Bands period
input double          BollingerDeviation         = 2.0;            // Bollinger Bands std deviation
input int             ATRPeriod                  = 14;             // ATR period
input double          SuperTrendMultiplier       = 2.5;            // SuperTrend ATR multiplier
input int             TenkanSen                  = 9;              // Ichimoku Tenkan-sen
input int             KijunSen                   = 26;             // Ichimoku Kijun-sen
input int             SenkouSpanB                = 52;             // Ichimoku Senkou Span B

//--- Input Parameters: Institutional Risk & Prop-Firm Guard
input double          MaxRisk                    = 1.0;            // Base risk per trade (%)
input double          AdaptiveRiskMultiplier     = 1.4;            // Multiplier for high-confluence signals
input double          ATRMultiplier              = 2.0;            // ATR multiplier for Stop Loss
input int             Slippage                   = 3;              // Max slippage in points
input double          MaxDrawdown                = 4.5;            // Max daily drawdown limit (%)
input double          MaxTotalDrawdown           = 9.0;            // Max overall trailing drawdown (%)
input double          KellyFactor                = 0.35;           // Fractional Kelly safety factor
input int             MaxDailyTrades             = 6;              // Max trades per day
input int             MinBarsSinceLastTrade      = 3;              // Cooldown bars between trades
input int             MaxSpread                  = 20;             // Maximum allowed spread in points
input double          MinNeuralWinProb           = 0.54;           // Minimum Neural Scorer win probability

//--- Input Parameters: Smart Exit Management
input double          RiskRewardRatio            = 2.2;            // Target Risk-to-Reward ratio
input bool            UseBreakEven               = true;           // Enable Break-Even + Commission lock
input double          BreakEvenTriggerPips       = 14.0;           // Pips profit to trigger Break-Even
input double          BreakEvenPlusPips          = 2.0;            // Extra pips locked at Break-Even
input bool            UsePartialTakeProfit       = true;           // Scale out 40% at 1.0R
input double          TrailingStopActivationPips = 20.0;           // Pips profit to activate Smart Trail
input double          TrailingStopDistance       = 12.0;           // Base trailing stop distance in pips
input int             Magic                      = 202504;         // Expert Advisor Magic Number

#define BUFFER_SIZE 100

//--- Native MQL5 Trading & Indicator Handles
CTrade                  g_trade;
CPositionInfo           g_posInfo;
