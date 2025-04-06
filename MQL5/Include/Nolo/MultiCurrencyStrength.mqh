//+------------------------------------------------------------------+
//|                                        MultiCurrencyStrength.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|      G8 Currency Strength Index & Pair Divergence Calculator     |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_MULTI_CURRENCY_STRENGTH_MQH
#define NOLO_MULTI_CURRENCY_STRENGTH_MQH

class CMultiCurrencyStrength
{
private:
   int m_lookbackBars;

public:
   CMultiCurrencyStrength(int lookbackBars = 20)
   {
      m_lookbackBars = MathMax(5, lookbackBars);
   }

   double GetPairMomentumScore(const double &closes[])
   {
