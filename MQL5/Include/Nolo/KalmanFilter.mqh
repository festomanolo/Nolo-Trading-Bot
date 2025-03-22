//+------------------------------------------------------------------+
//|                                                 KalmanFilter.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|         State-Space 2D Kinematic Kalman Filter (Level & Velocity)|
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_KALMAN_FILTER_MQH
#define NOLO_KALMAN_FILTER_MQH

class CKalmanTrendTracker
{
private:
   bool   m_initialized;
   double m_level;
