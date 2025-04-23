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

