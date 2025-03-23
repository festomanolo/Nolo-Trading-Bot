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
   double m_velocity;
   double m_p00, m_p01, m_p10, m_p11;
   double m_processNoise;
   double m_measurementNoise;
   double m_ewmaInnovationSq;

public:
   CKalmanTrendTracker(double processNoise = 0.0001, double measurementNoise = 0.01)
   {
