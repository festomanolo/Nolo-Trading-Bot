//+------------------------------------------------------------------+
//|                                      RiskAndPortfolioManager.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|    Bayesian Kelly, Prop-Firm Drawdown Guard & Lot Normalization  |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_RISK_AND_PORTFOLIO_MANAGER_MQH
#define NOLO_RISK_AND_PORTFOLIO_MANAGER_MQH

#include "CoreTypes.mqh"

class CRiskAndPortfolioManager
{
private:
   double m_highWaterMark;
   double m_dayStartBalance;
   int    m_currentDayOfYear;
   int    m_tradesToday;
   int    m_totalTrades;
   int    m_winningTrades;
   int    m_consecutiveWins;
   int    m_consecutiveLosses;
   double m_betaAlpha;
   double m_betaBeta;

public:
   CRiskAndPortfolioManager()
   {
      m_highWaterMark     = 0.0;
      m_dayStartBalance   = 0.0;
      m_currentDayOfYear  = -1;
      m_tradesToday       = 0;
      m_totalTrades       = 0;
      m_winningTrades     = 0;
      m_consecutiveWins   = 0;
      m_consecutiveLosses = 0;
      m_betaAlpha         = 6.0;
      m_betaBeta          = 4.0;
