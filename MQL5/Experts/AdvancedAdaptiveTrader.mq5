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
