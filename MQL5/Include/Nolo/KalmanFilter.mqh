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
      m_processNoise = MathMax(1e-9, processNoise);
      m_measurementNoise = MathMax(1e-9, measurementNoise);
      Reset();
   }

   void Reset()
   {
      m_initialized = false;
      m_level = 0.0;
      m_velocity = 0.0;
      m_p00 = 1.0;
      m_p01 = 0.0;
      m_p10 = 0.0;
      m_p11 = 1.0;
      m_ewmaInnovationSq = m_measurementNoise;
   }

   double Update(double price, double dt = 1.0)
   {
      if(!m_initialized)
      {
         m_level = price;
         m_velocity = 0.0;
         m_p00 = m_measurementNoise;
         m_p01 = 0.0;
         m_p10 = 0.0;
         m_p11 = m_processNoise;
         m_initialized = true;
         return m_level;
      }

      // 1. State prediction x_{k|k-1} = F * x_{k-1|k-1}
      double predLevel = m_level + m_velocity * dt;
      double predVel   = m_velocity;

      double dt2 = dt * dt;
      double dt3 = dt2 * dt * 0.5;
      double dt4 = dt2 * dt2 * 0.25;

      double q00 = m_processNoise * dt4;
      double q01 = m_processNoise * dt3;
      double q11 = m_processNoise * dt2;

      double p00Pred = m_p00 + dt * (m_p10 + m_p01) + dt2 * m_p11 + q00;
      double p01Pred = m_p01 + dt * m_p11 + q01;
      double p10Pred = m_p10 + dt * m_p11 + q01;
      double p11Pred = m_p11 + q11;

      // 2. Innovation residual
      double innovation = price - predLevel;
      m_ewmaInnovationSq = 0.92 * m_ewmaInnovationSq + 0.08 * (innovation * innovation);
      double noiseScale = MathMin(5.0, MathMax(0.5, m_ewmaInnovationSq / MathMax(1e-12, m_measurementNoise)));
      double rEff = m_measurementNoise * noiseScale;

      double s = MathMax(1e-12, p00Pred + rEff);
      double k0 = p00Pred / s;
      double k1 = p10Pred / s;

      // 3. State & covariance update
