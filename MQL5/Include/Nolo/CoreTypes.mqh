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
