//+------------------------------------------------------------------+
//|                                           NeuralSignalScorer.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|     Online 2-Layer Neural Perceptron & Logistic Signal Scorer    |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_NEURAL_SIGNAL_SCORER_MQH
#define NOLO_NEURAL_SIGNAL_SCORER_MQH

class CNeuralSignalScorer
{
private:
   double m_wTrend;
   double m_wKalman;
   double m_wHurst;
   double m_wADX;
   double m_wSMC;
   double m_wOrderFlow;
   double m_wHTF;
   double m_bias;
   double m_learningRate;

   double Sigmoid(double z)
   {
      double clamped = MathMax(-15.0, MathMin(15.0, z));
      return 1.0 / (1.0 + MathExp(-clamped));
   }

   double LeakyReLU(double x)
   {
      return (x >= 0.0) ? x : 0.15 * x;
