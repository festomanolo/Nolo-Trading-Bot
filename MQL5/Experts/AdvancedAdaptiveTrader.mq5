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
