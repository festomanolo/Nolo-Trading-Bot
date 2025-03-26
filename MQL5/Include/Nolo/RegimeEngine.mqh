//+------------------------------------------------------------------+
//|                                                 RegimeEngine.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|   Multi-Factor Regime Classifier (Hurst, Efficiency, ADX, Kalman)|
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_REGIME_ENGINE_MQH
#define NOLO_REGIME_ENGINE_MQH

#include "CoreTypes.mqh"
#include "KalmanFilter.mqh"

class CRegimeEngine
{
private:
   CKalmanTrendTracker m_kalman;
   string              m_lastRegime;

public:
   CRegimeEngine()
   {
      m_lastRegime = "MIXED";
