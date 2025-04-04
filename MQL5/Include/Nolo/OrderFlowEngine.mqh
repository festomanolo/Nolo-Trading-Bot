//+------------------------------------------------------------------+
//|                                              OrderFlowEngine.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|      Intrabar Volume Delta, Buying Pressure, and VPIN Estimator  |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_ORDER_FLOW_ENGINE_MQH
#define NOLO_ORDER_FLOW_ENGINE_MQH

class COrderFlowEngine
{
public:
   double ComputeBuyPressureRatio(
      const double &highs[],
      const double &lows[],
      const double &closes[],
      const long   &volumes[],
      int window = 10)
   {
      int limit = MathMin(window, ArraySize(closes));
      if(limit <= 0) return 0.50;

