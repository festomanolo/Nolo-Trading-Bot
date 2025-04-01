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
