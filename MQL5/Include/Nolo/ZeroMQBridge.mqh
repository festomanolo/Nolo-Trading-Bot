//+------------------------------------------------------------------+
//|                                                 ZeroMQBridge.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|      Real-Time Shared Telemetry Bridge to Python Quant Engine    |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_ZEROMQ_BRIDGE_MQH
#define NOLO_ZEROMQ_BRIDGE_MQH

#include "CoreTypes.mqh"

class CPythonTelemetryBridge
{
private:
   bool m_enabled;

public:
   CPythonTelemetryBridge(bool enabled = false)
   {
      m_enabled = enabled;
   }

   bool WriteHeartbeat(string symbol, const NoloRegimeSnapshot &regime, double bid, double ask)
