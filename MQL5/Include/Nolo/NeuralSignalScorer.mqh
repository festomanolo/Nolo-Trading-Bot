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
