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
   }

   double ComputeHurstExponent(const double &closes[], int count)
   {
      if(count < 24) return 0.50;
      int n = count - 1;
      double returns[];
      ArrayResize(returns, n);
      double sumRet = 0.0;

      for(int i = 0; i < n; i++)
      {
         double p0 = MathMax(1e-9, closes[i + 1]);
         double p1 = MathMax(1e-9, closes[i]);
         returns[i] = MathLog(p1 / p0);
         sumRet += returns[i];
      }

      double meanRet = sumRet / n;
      double cumDev = 0.0;
      double maxDev = -1e9;
      double minDev = 1e9;
      double varSum = 0.0;

      for(int i = 0; i < n; i++)
      {
         double centered = returns[i] - meanRet;
         cumDev += centered;
         if(cumDev > maxDev) maxDev = cumDev;
         if(cumDev < minDev) minDev = cumDev;
         varSum += centered * centered;
      }

      double rangeR = maxDev - minDev;
      double stdS = MathSqrt(varSum / n);
      if(stdS <= 1e-12 || rangeR <= 0.0) return 0.50;

      double h = MathLog(rangeR / stdS) / MathLog((double)n);
      return MathMax(0.05, MathMin(0.95, h));
   }

   double ComputeEfficiencyRatio(const double &closes[], int period = 14)
   {
      if(ArraySize(closes) <= period) return 0.30;
      double netChange = MathAbs(closes[0] - closes[period]);
      double pathLen = 0.0;
      for(int i = 0; i < period; i++)
         pathLen += MathAbs(closes[i] - closes[i + 1]);

      if(pathLen <= 1e-12) return 0.0;
      return MathMax(0.0, MathMin(1.0, netChange / pathLen));
   }

   void EvaluateRegime(
      const double &closes[],
      const double &highs[],
      const double &lows[],
      const double &fastMA[],
      const double &slowMA[],
      const double &upperBB[],
      const double &lowerBB[],
      const double &atr[],
      double adxValue,
      double plusDI,
      double minusDI,
      bool hasRecentHH,
      bool hasRecentLL,
      NoloRegimeSnapshot &outSnap)
   {
      double currATR = MathMax(1e-9, atr[0]);
      double avgATR = 0.0;
      for(int i = 0; i < 20 && i < ArraySize(atr); i++)
         avgATR += atr[i];
      avgATR /= 20.0;

      double atrRatio = currATR / MathMax(1e-9, avgATR);
      double bbWidth = ((upperBB[0] - lowerBB[0]) / MathMax(1e-9, closes[0])) * 100.0;
      double hurst = ComputeHurstExponent(closes, MathMin(64, ArraySize(closes)));
      double er = ComputeEfficiencyRatio(closes, 14);

      m_kalman.Reset();
      int kStart = MathMin(30, ArraySize(closes) - 1);
      for(int i = kStart; i >= 0; i--)
         m_kalman.Update(closes[i]);
      double kalmanSlope = m_kalman.GetVelocity() / currATR;

      bool maBull = (fastMA[0] > slowMA[0]);
      bool maBear = (fastMA[0] < slowMA[0]);

      if(adxValue > 24.0 && maBull && plusDI >= minusDI && (hurst >= 0.48 || er >= 0.30))
      {
         outSnap.regimeName = "TREND_UP";
         outSnap.confidence = MathMin(0.95, 0.55 + (adxValue - 20.0) / 60.0 + (hurst - 0.5));
      }
      else if(adxValue > 24.0 && maBear && minusDI > plusDI && (hurst >= 0.48 || er >= 0.30))
      {
         outSnap.regimeName = "TREND_DOWN";
         outSnap.confidence = MathMin(0.95, 0.55 + (adxValue - 20.0) / 60.0 + (hurst - 0.5));
      }
