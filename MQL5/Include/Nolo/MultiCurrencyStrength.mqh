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
      if(ArraySize(closes) <= m_lookbackBars) return 0.0;
      double p0 = MathMax(1e-9, closes[m_lookbackBars]);
      double p1 = closes[0];
      double pctChange = ((p1 - p0) / p0) * 100.0;
      return MathMax(-100.0, MathMin(100.0, pctChange * 40.0));
   }
};

#endif // NOLO_MULTI_CURRENCY_STRENGTH_MQH
