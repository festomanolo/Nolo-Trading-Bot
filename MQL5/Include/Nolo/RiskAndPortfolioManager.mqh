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
   }

   void Initialize(double currentBalance)
   {
      m_highWaterMark   = currentBalance;
      m_dayStartBalance = currentBalance;
   }

   void OnTickRefresh(datetime currentTime, double balance, double equity)
   {
      MqlDateTime dt;
      TimeToStruct(currentTime, dt);
      if(dt.day_of_year != m_currentDayOfYear)
      {
         m_currentDayOfYear = dt.day_of_year;
         m_dayStartBalance  = MathMax(balance, equity);
         m_tradesToday      = 0;
      }
      if(equity > m_highWaterMark)
         m_highWaterMark = equity;
   }

   void RecordTradeOpened() { m_tradesToday++; }

   void RecordTradeOutcome(bool isWin)
   {
      m_totalTrades++;
      if(isWin)
      {
         m_winningTrades++;
         m_consecutiveWins++;
         m_consecutiveLosses = 0;
         m_betaAlpha = m_betaAlpha * 0.98 + 1.0;
         m_betaBeta  = m_betaBeta  * 0.98;
      }
      else
      {
         m_consecutiveLosses++;
         m_consecutiveWins = 0;
         m_betaAlpha = m_betaAlpha * 0.98;
         m_betaBeta  = m_betaBeta  * 0.98 + 1.0;
      }
   }

   double GetBayesianWinRate() const
   {
      return m_betaAlpha / MathMax(1e-9, m_betaAlpha + m_betaBeta);
   }

   int GetTradesToday() const { return m_tradesToday; }

   bool IsDrawdownExceeded(double currentEquity, double maxDailyDDPct, double maxTotalDDPct)
   {
      if(m_dayStartBalance > 0.0)
      {
         double dailyLossPct = ((m_dayStartBalance - currentEquity) / m_dayStartBalance) * 100.0;
