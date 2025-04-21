//+------------------------------------------------------------------+
//|                                                 DashboardHUD.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|      Real-Time On-Chart Institutional Telemetry HUD Overlay      |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_DASHBOARD_HUD_MQH
#define NOLO_DASHBOARD_HUD_MQH

#include "CoreTypes.mqh"

class CDashboardHUD
{
private:
   bool m_enabled;

public:
   CDashboardHUD(bool enabled = true)
   {
      m_enabled = enabled;
   }

   void Render(
      string symbol,
      const NoloRegimeSnapshot &regime,
      double winRate,
      double neuralProb,
      double buyPressure,
      int tradesToday,
      int maxDailyTrades,
      double equity,
      double balance)
   {
      if(!m_enabled) return;

      string hud = StringFormat(
         "╔══════════════════════════════════════════════════════════╗\n"
         "║ NOLO TRADING BOT v4.0 — INSTITUTIONAL QUANT ENGINE       ║\n"
         "╠══════════════════════════════════════════════════════════╣\n"
         "║ Symbol         : %-10s | Regime    : %-14s ║\n"
         "║ Regime Conf    : %5.1f%%     | Hurst H   : %6.3f         ║\n"
         "║ Efficiency ER  : %5.3f      | ADX (14)  : %6.2f         ║\n"
         "║ Kalman Slope   : %+6.3f     | ATR Ratio : %6.2fx        ║\n"
         "║ OrderFlow Buy  : %5.1f%%     | Neural P  : %5.1f%%         ║\n"
         "║ Bayesian WinR  : %5.1f%%     | Daily Trd : %d / %d          ║\n"
         "║ Balance        : $%9.2f | Equity    : $%9.2f     ║\n"
         "╚══════════════════════════════════════════════════════════╝",
         symbol,
         regime.regimeName,
         regime.confidence * 100.0,
         regime.hurstExponent,
         regime.efficiencyRatio,
         regime.adxValue,
         regime.kalmanVelocity,
         regime.atrRatio,
         buyPressure * 100.0,
