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
