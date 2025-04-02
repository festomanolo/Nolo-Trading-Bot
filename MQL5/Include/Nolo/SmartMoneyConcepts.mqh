//+------------------------------------------------------------------+
//|                                           SmartMoneyConcepts.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|      Order Blocks (OB), Fair Value Gaps (FVG) & Liquidity Sweeps |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_SMART_MONEY_CONCEPTS_MQH
#define NOLO_SMART_MONEY_CONCEPTS_MQH

#include "CoreTypes.mqh"

class CSmartMoneyConcepts
{
private:
   double m_fvgMinAtrFraction;
   double m_sweepWickRatio;

public:
   CSmartMoneyConcepts(double fvgAtrFrac = 0.25, double sweepWickRatio = 0.45)
   {
      m_fvgMinAtrFraction = fvgAtrFrac;
      m_sweepWickRatio = sweepWickRatio;
   }

   bool DetectBullishFVG(const double &highs[], const double &lows[], const double &closes[], const double &opens[], double atr, int shift = 0)
   {
      if(ArraySize(lows) <= shift + 2) return false;
      double gap = lows[shift] - highs[shift + 2];
      bool middleBullish = closes[shift + 1] > opens[shift + 1];
      return (gap >= atr * m_fvgMinAtrFraction && middleBullish);
   }

   bool DetectBearishFVG(const double &highs[], const double &lows[], const double &closes[], const double &opens[], double atr, int shift = 0)
   {
      if(ArraySize(highs) <= shift + 2) return false;
      double gap = lows[shift + 2] - highs[shift];
      bool middleBearish = closes[shift + 1] < opens[shift + 1];
      return (gap >= atr * m_fvgMinAtrFraction && middleBearish);
   }

   bool DetectBullishLiquiditySweep(const double &highs[], const double &lows[], const double &closes[], const double &opens[], int lookback = 15)
   {
      if(ArraySize(lows) <= lookback) return false;
      double priorLow = lows[1];
      for(int i = 2; i <= lookback; i++)
      {
         if(lows[i] < priorLow) priorLow = lows[i];
      }
      double rng = MathMax(1e-9, highs[0] - lows[0]);
      double lowerWick = MathMin(opens[0], closes[0]) - lows[0];
      return (lows[0] < priorLow && closes[0] > priorLow && (lowerWick / rng) >= m_sweepWickRatio);
   }

   bool DetectBearishLiquiditySweep(const double &highs[], const double &lows[], const double &closes[], const double &opens[], int lookback = 15)
   {
      if(ArraySize(highs) <= lookback) return false;
      double priorHigh = highs[1];
      for(int i = 2; i <= lookback; i++)
      {
         if(highs[i] > priorHigh) priorHigh = highs[i];
      }
      double rng = MathMax(1e-9, highs[0] - lows[0]);
