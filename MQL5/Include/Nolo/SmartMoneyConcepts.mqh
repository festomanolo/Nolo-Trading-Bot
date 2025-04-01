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
