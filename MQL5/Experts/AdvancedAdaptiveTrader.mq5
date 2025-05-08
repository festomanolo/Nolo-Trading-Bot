//+------------------------------------------------------------------+
//|                                       AdvancedAdaptiveTrader.mq5 |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|    Multi-Strategy Real-Time Adaptive Forex Expert Advisor (MT5)  |
//+------------------------------------------------------------------+
#property copyright   "Nolo Quantitative Systems 2025"
#property link        "https://github.com/festomanolo/Nolo-Trading-Bot"
#property version     "4.00"
#property description "Institutional Adaptive Forex EA: Kalman Filter, Hurst Exponent, SMC (OB/FVG/Sweep), Order Flow, Online Neural Scorer & Prop-Firm Risk Engine"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <Trade\AccountInfo.mqh>

#include "..\Include\Nolo\CoreTypes.mqh"
#include "..\Include\Nolo\KalmanFilter.mqh"
#include "..\Include\Nolo\RegimeEngine.mqh"
#include "..\Include\Nolo\SmartMoneyConcepts.mqh"
#include "..\Include\Nolo\OrderFlowEngine.mqh"
#include "..\Include\Nolo\MultiCurrencyStrength.mqh"
#include "..\Include\Nolo\NeuralSignalScorer.mqh"
#include "..\Include\Nolo\NewsCalendarGuard.mqh"
#include "..\Include\Nolo\RiskAndPortfolioManager.mqh"
#include "..\Include\Nolo\DashboardHUD.mqh"
#include "..\Include\Nolo\ZeroMQBridge.mqh"

//--- Input Parameters: Strategy & Intelligence
input REGIME_TYPE     MarketRegimeMode           = ADAPTIVE;       // Market Regime Detection Mode
input RISK_MODEL      RiskModelType              = BAYESIAN_KELLY; // Institutional Risk Sizing Model
input bool            UseVolatilityFilter        = true;           // Filter entries during extreme chop
input bool            UsePriceMomentum           = true;           // Confirm with Kalman & OrderFlow momentum
input bool            UseMarketStructure         = true;           // Use SMC Swing/OB/FVG structure stops
input bool            UseAlternateTimeframes     = true;           // Multi-timeframe (HTF) confirmation
input bool            UseSmartTrailingStop       = true;           // Volatility-adaptive ATR trailing stop
input bool            UseNeuralScorer            = true;           // Online Neural Perceptron signal filter
input bool            UseNewsCalendarGuard       = true;           // High-impact macro news & rollover guard
input bool            ShowDashboardHUD           = true;           // Render real-time on-chart telemetry HUD
input bool            EnablePythonBridge         = false;          // Publish telemetry to Python Quant Engine

//--- Input Parameters: Timeframes & Moving Averages
input ENUM_TIMEFRAMES MainTimeframe              = PERIOD_M5;      // Main trading timeframe
input ENUM_TIMEFRAMES HigherTimeframe            = PERIOD_H1;      // Higher confirmation timeframe
input int             FastMAPeriod               = 8;              // Fast EMA period
input int             SlowMAPeriod               = 21;             // Slow EMA period
input ENUM_MA_METHOD  FastMAMethod               = MODE_EMA;       // Fast MA method
input ENUM_MA_METHOD  SlowMAMethod               = MODE_EMA;       // Slow MA method

//--- Input Parameters: Oscillators & MACD
input int             RSIPeriod                  = 14;             // RSI period
input int             RSI_UpperLevel             = 70;             // RSI upper threshold
input int             RSI_LowerLevel             = 30;             // RSI lower threshold
input int             StochasticKPeriod          = 5;              // Stochastic %K period
input int             StochasticDPeriod          = 3;              // Stochastic %D period
input int             StochasticSlowing          = 3;              // Stochastic slowing
input int             MACD_FastEMA               = 12;             // MACD Fast EMA
input int             MACD_SlowEMA               = 26;             // MACD Slow EMA
input int             MACD_SignalSMA             = 9;              // MACD Signal SMA

//--- Input Parameters: Volatility, SuperTrend & Ichimoku
input int             BollingerPeriod            = 20;             // Bollinger Bands period
input double          BollingerDeviation         = 2.0;            // Bollinger Bands std deviation
input int             ATRPeriod                  = 14;             // ATR period
input double          SuperTrendMultiplier       = 2.5;            // SuperTrend ATR multiplier
input int             TenkanSen                  = 9;              // Ichimoku Tenkan-sen
input int             KijunSen                   = 26;             // Ichimoku Kijun-sen
input int             SenkouSpanB                = 52;             // Ichimoku Senkou Span B

//--- Input Parameters: Institutional Risk & Prop-Firm Guard
input double          MaxRisk                    = 1.0;            // Base risk per trade (%)
input double          AdaptiveRiskMultiplier     = 1.4;            // Multiplier for high-confluence signals
input double          ATRMultiplier              = 2.0;            // ATR multiplier for Stop Loss
input int             Slippage                   = 3;              // Max slippage in points
input double          MaxDrawdown                = 4.5;            // Max daily drawdown limit (%)
input double          MaxTotalDrawdown           = 9.0;            // Max overall trailing drawdown (%)
input double          KellyFactor                = 0.35;           // Fractional Kelly safety factor
input int             MaxDailyTrades             = 6;              // Max trades per day
input int             MinBarsSinceLastTrade      = 3;              // Cooldown bars between trades
input int             MaxSpread                  = 20;             // Maximum allowed spread in points
input double          MinNeuralWinProb           = 0.54;           // Minimum Neural Scorer win probability

//--- Input Parameters: Smart Exit Management
input double          RiskRewardRatio            = 2.2;            // Target Risk-to-Reward ratio
input bool            UseBreakEven               = true;           // Enable Break-Even + Commission lock
input double          BreakEvenTriggerPips       = 14.0;           // Pips profit to trigger Break-Even
input double          BreakEvenPlusPips          = 2.0;            // Extra pips locked at Break-Even
input bool            UsePartialTakeProfit       = true;           // Scale out 40% at 1.0R
input double          TrailingStopActivationPips = 20.0;           // Pips profit to activate Smart Trail
input double          TrailingStopDistance       = 12.0;           // Base trailing stop distance in pips
input int             Magic                      = 202504;         // Expert Advisor Magic Number

#define BUFFER_SIZE 100

//--- Native MQL5 Trading & Indicator Handles
CTrade                  g_trade;
CPositionInfo           g_posInfo;
CRegimeEngine           g_regimeEngine;
CSmartMoneyConcepts     g_smcEngine;
COrderFlowEngine        g_orderFlow;
CMultiCurrencyStrength  g_currencyMeter;
CNeuralSignalScorer     g_neuralScorer;
CNewsCalendarGuard      g_newsGuard;
CRiskAndPortfolioManager g_riskManager;
CDashboardHUD           g_hud;
CPythonTelemetryBridge  g_pyBridge;

int g_hFastMA, g_hSlowMA, g_hHTFFastMA, g_hHTFSlowMA;
int g_hRSI, g_hMACD, g_hBB, g_hATR, g_hADX, g_hStoch, g_hIchimoku;

double FastMA[], SlowMA[], RSIValue[], MACDMain[], MACDSignal[], UpperBB[], LowerBB[], ATRValue[];
double ADXMain[], PlusDI[], MinusDI[], StochMain[], StochSignal[];
double IchimokuTenkan[], IchimokuKijun[], IchimokuSenkouA[], IchimokuSenkouB[];
double SuperTrendValue[], SuperTrendDirection[];
double CloseArr[], HighArr[], LowArr[], OpenArr[];
long   VolumeArr[];

NoloRegimeSnapshot g_currentRegime;
datetime           g_lastTradeTime = 0;
double             g_lastNeuralProb = 0.60;
double             g_lastBuyPressure = 0.50;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   if(FastMAPeriod >= SlowMAPeriod)
   {
      Print("Error: FastMAPeriod must be strictly less than SlowMAPeriod.");
      return(INIT_PARAMETERS_INCORRECT);
   }

   g_trade.SetExpertMagicNumber(Magic);
   g_trade.SetDeviationInPoints(Slippage);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   g_hFastMA    = iMA(_Symbol, MainTimeframe, FastMAPeriod, 0, FastMAMethod, PRICE_CLOSE);
   g_hSlowMA    = iMA(_Symbol, MainTimeframe, SlowMAPeriod, 0, SlowMAMethod, PRICE_CLOSE);
   g_hHTFFastMA = iMA(_Symbol, HigherTimeframe, FastMAPeriod, 0, FastMAMethod, PRICE_CLOSE);
   g_hHTFSlowMA = iMA(_Symbol, HigherTimeframe, SlowMAPeriod, 0, SlowMAMethod, PRICE_CLOSE);
   g_hRSI       = iRSI(_Symbol, MainTimeframe, RSIPeriod, PRICE_CLOSE);
   g_hMACD      = iMACD(_Symbol, MainTimeframe, MACD_FastEMA, MACD_SlowEMA, MACD_SignalSMA, PRICE_CLOSE);
   g_hBB        = iBands(_Symbol, MainTimeframe, BollingerPeriod, 0, BollingerDeviation, PRICE_CLOSE);
   g_hATR       = iATR(_Symbol, MainTimeframe, ATRPeriod);
   g_hADX       = iADX(_Symbol, MainTimeframe, 14);
   g_hStoch     = iStochastic(_Symbol, MainTimeframe, StochasticKPeriod, StochasticDPeriod, StochasticSlowing, MODE_SMA, STO_LOWHIGH);
   g_hIchimoku  = iIchimoku(_Symbol, MainTimeframe, TenkanSen, KijunSen, SenkouSpanB);

   if(g_hFastMA == INVALID_HANDLE || g_hSlowMA == INVALID_HANDLE || g_hRSI == INVALID_HANDLE ||
      g_hMACD == INVALID_HANDLE || g_hBB == INVALID_HANDLE || g_hATR == INVALID_HANDLE)
   {
      Print("Error initializing native MQL5 indicator handles.");
      return(INIT_FAILED);
   }

   ArrayResize(SuperTrendValue, BUFFER_SIZE);
   ArrayResize(SuperTrendDirection, BUFFER_SIZE);

   g_riskManager.Initialize(AccountInfoDouble(ACCOUNT_BALANCE));
   g_hud = CDashboardHUD(ShowDashboardHUD);
   g_pyBridge = CPythonTelemetryBridge(EnablePythonBridge);

   Print("Nolo Trading Bot v4.0 (AdvancedAdaptiveTrader) initialized successfully.");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   IndicatorRelease(g_hFastMA);
   IndicatorRelease(g_hSlowMA);
   IndicatorRelease(g_hHTFFastMA);
   IndicatorRelease(g_hHTFSlowMA);
   IndicatorRelease(g_hRSI);
   IndicatorRelease(g_hMACD);
   IndicatorRelease(g_hBB);
   IndicatorRelease(g_hATR);
   IndicatorRelease(g_hADX);
   IndicatorRelease(g_hStoch);
   IndicatorRelease(g_hIchimoku);
   g_hud.Clear();
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
   g_riskManager.OnTickRefresh(TimeCurrent(), balance, equity);

   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > MaxSpread) return;

   if(g_riskManager.IsDrawdownExceeded(equity, MaxDrawdown, MaxTotalDrawdown))
      return;

   if(!UpdateAllBuffers()) return;

   bool hasHH = HasRecentHigherHigh(12);
   bool hasLL = HasRecentLowerLow(12);
   g_regimeEngine.EvaluateRegime(
      CloseArr, HighArr, LowArr, FastMA, SlowMA, UpperBB, LowerBB, ATRValue,
      ADXMain[0], PlusDI[0], MinusDI[0], hasHH, hasLL, g_currentRegime
   );

   g_lastBuyPressure = g_orderFlow.ComputeBuyPressureRatio(HighArr, LowArr, CloseArr, VolumeArr, 10);

   ManageOpenPositions();

   g_hud.Render(
      _Symbol, g_currentRegime, g_riskManager.GetBayesianWinRate(),
      g_lastNeuralProb, g_lastBuyPressure, g_riskManager.GetTradesToday(),
      MaxDailyTrades, equity, balance
   );

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   g_pyBridge.WriteHeartbeat(_Symbol, g_currentRegime, bid, ask);

   if(g_riskManager.GetTradesToday() >= MaxDailyTrades) return;
   if(BarsSinceLastTrade() < MinBarsSinceLastTrade) return;
   if(UseNewsCalendarGuard && g_newsGuard.IsHighImpactNewsWindow(_Symbol, TimeCurrent())) return;

   CheckEntrySignals();
}

//+------------------------------------------------------------------+
//| Refresh all MQL5 indicator and price series buffers              |
//+------------------------------------------------------------------+
bool UpdateAllBuffers()
{
   ArraySetAsSeries(FastMA, true);
   ArraySetAsSeries(SlowMA, true);
   ArraySetAsSeries(RSIValue, true);
   ArraySetAsSeries(MACDMain, true);
   ArraySetAsSeries(MACDSignal, true);
   ArraySetAsSeries(UpperBB, true);
   ArraySetAsSeries(LowerBB, true);
   ArraySetAsSeries(ATRValue, true);
   ArraySetAsSeries(ADXMain, true);
   ArraySetAsSeries(PlusDI, true);
   ArraySetAsSeries(MinusDI, true);
   ArraySetAsSeries(StochMain, true);
   ArraySetAsSeries(StochSignal, true);
   ArraySetAsSeries(IchimokuTenkan, true);
   ArraySetAsSeries(IchimokuKijun, true);
   ArraySetAsSeries(IchimokuSenkouA, true);
   ArraySetAsSeries(IchimokuSenkouB, true);
   ArraySetAsSeries(CloseArr, true);
   ArraySetAsSeries(HighArr, true);
   ArraySetAsSeries(LowArr, true);
   ArraySetAsSeries(OpenArr, true);
   ArraySetAsSeries(VolumeArr, true);

   if(CopyClose(_Symbol, MainTimeframe, 0, BUFFER_SIZE, CloseArr) < BUFFER_SIZE) return false;
   if(CopyHigh(_Symbol, MainTimeframe, 0, BUFFER_SIZE, HighArr) < BUFFER_SIZE) return false;
   if(CopyLow(_Symbol, MainTimeframe, 0, BUFFER_SIZE, LowArr) < BUFFER_SIZE) return false;
   if(CopyOpen(_Symbol, MainTimeframe, 0, BUFFER_SIZE, OpenArr) < BUFFER_SIZE) return false;
   if(CopyTickVolume(_Symbol, MainTimeframe, 0, BUFFER_SIZE, VolumeArr) < BUFFER_SIZE) return false;

   if(CopyBuffer(g_hFastMA, 0, 0, BUFFER_SIZE, FastMA) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hSlowMA, 0, 0, BUFFER_SIZE, SlowMA) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hRSI, 0, 0, BUFFER_SIZE, RSIValue) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hMACD, 0, 0, BUFFER_SIZE, MACDMain) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hMACD, 1, 0, BUFFER_SIZE, MACDSignal) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hBB, 1, 0, BUFFER_SIZE, UpperBB) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hBB, 2, 0, BUFFER_SIZE, LowerBB) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hATR, 0, 0, BUFFER_SIZE, ATRValue) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hADX, 0, 0, BUFFER_SIZE, ADXMain) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hADX, 1, 0, BUFFER_SIZE, PlusDI) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hADX, 2, 0, BUFFER_SIZE, MinusDI) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hStoch, 0, 0, BUFFER_SIZE, StochMain) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hStoch, 1, 0, BUFFER_SIZE, StochSignal) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hIchimoku, 0, 0, BUFFER_SIZE, IchimokuTenkan) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hIchimoku, 1, 0, BUFFER_SIZE, IchimokuKijun) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hIchimoku, 2, 0, BUFFER_SIZE, IchimokuSenkouA) < BUFFER_SIZE) return false;
   if(CopyBuffer(g_hIchimoku, 3, 0, BUFFER_SIZE, IchimokuSenkouB) < BUFFER_SIZE) return false;

   CalculateSuperTrendSeries();
   return true;
}

//+------------------------------------------------------------------+
//| Ratcheting SuperTrend calculation from oldest to newest bar      |
//+------------------------------------------------------------------+
void CalculateSuperTrendSeries()
{
   double finalUpper[], finalLower[];
   ArrayResize(finalUpper, BUFFER_SIZE);
   ArrayResize(finalLower, BUFFER_SIZE);

   for(int i = BUFFER_SIZE - 1; i >= 0; i--)
   {
      double hl2 = (HighArr[i] + LowArr[i]) * 0.5;
      double basicUpper = hl2 + SuperTrendMultiplier * ATRValue[i];
      double basicLower = hl2 - SuperTrendMultiplier * ATRValue[i];

      if(i == BUFFER_SIZE - 1)
      {
         finalUpper[i] = basicUpper;
         finalLower[i] = basicLower;
         SuperTrendDirection[i] = 1.0;
         SuperTrendValue[i] = finalLower[i];
         continue;
      }

      double prevClose = CloseArr[i + 1];
      finalUpper[i] = (basicUpper < finalUpper[i + 1] || prevClose > finalUpper[i + 1]) ? basicUpper : finalUpper[i + 1];
      finalLower[i] = (basicLower > finalLower[i + 1] || prevClose < finalLower[i + 1]) ? basicLower : finalLower[i + 1];

      double prevDir = SuperTrendDirection[i + 1];
      if(prevDir < 0 && CloseArr[i] > finalUpper[i + 1])
         SuperTrendDirection[i] = 1.0;
      else if(prevDir > 0 && CloseArr[i] < finalLower[i + 1])
         SuperTrendDirection[i] = -1.0;
      else
         SuperTrendDirection[i] = prevDir;

      SuperTrendValue[i] = (SuperTrendDirection[i] > 0) ? finalLower[i] : finalUpper[i];
   }
}

bool HasRecentHigherHigh(int bars)
{
   double highest = HighArr[1];
   for(int i = 2; i < bars && i < BUFFER_SIZE; i++)
      if(HighArr[i] > highest) highest = HighArr[i];
   return CloseArr[0] > highest;
}

bool HasRecentLowerLow(int bars)
{
   double lowest = LowArr[1];
   for(int i = 2; i < bars && i < BUFFER_SIZE; i++)
      if(LowArr[i] < lowest) lowest = LowArr[i];
   return CloseArr[0] < lowest;
}

int BarsSinceLastTrade()
{
   if(g_lastTradeTime == 0) return 999;
   return Bars(_Symbol, MainTimeframe, g_lastTradeTime, TimeCurrent());
}

bool HasOpenPosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(g_posInfo.SelectByIndex(i))
      {
         if(g_posInfo.Symbol() == _Symbol && g_posInfo.Magic() == Magic)
            return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Manage open positions (Break-Even & Smart ATR Trailing Stop)     |
//+------------------------------------------------------------------+
void ManageOpenPositions()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits   = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double pip   = (digits == 3 || digits == 5) ? point * 10.0 : point;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!g_posInfo.SelectByIndex(i)) continue;
      if(g_posInfo.Symbol() != _Symbol || g_posInfo.Magic() != Magic) continue;

      ulong ticket     = g_posInfo.Ticket();
      double openPrice = g_posInfo.PriceOpen();
      double currSL    = g_posInfo.StopLoss();
      double currTP    = g_posInfo.TakeProfit();
      double markPrice = g_posInfo.PriceCurrent();

      double atrRatio = (ATRValue[10] > 1e-9) ? MathMax(0.65, MathMin(1.5, ATRValue[0] / ATRValue[10])) : 1.0;
      double adaptiveTrailPips = TrailingStopDistance * atrRatio;

      if(g_posInfo.PositionType() == POSITION_TYPE_BUY)
      {
         double pipsProfit = (markPrice - openPrice) / pip;
         if(UseBreakEven && pipsProfit >= BreakEvenTriggerPips && (currSL == 0.0 || currSL < openPrice))
         {
            double newSL = NormalizeDouble(openPrice + BreakEvenPlusPips * pip, digits);
            g_trade.PositionModify(ticket, newSL, currTP);
         }
         else if(UseSmartTrailingStop && pipsProfit >= TrailingStopActivationPips)
         {
            double newSL = NormalizeDouble(markPrice - adaptiveTrailPips * pip, digits);
            if(currSL == 0.0 || newSL > currSL + point * 2)
               g_trade.PositionModify(ticket, newSL, currTP);
         }
      }
      else if(g_posInfo.PositionType() == POSITION_TYPE_SELL)
      {
         double pipsProfit = (openPrice - markPrice) / pip;
         if(UseBreakEven && pipsProfit >= BreakEvenTriggerPips && (currSL == 0.0 || currSL > openPrice))
         {
            double newSL = NormalizeDouble(openPrice - BreakEvenPlusPips * pip, digits);
            g_trade.PositionModify(ticket, newSL, currTP);
         }
         else if(UseSmartTrailingStop && pipsProfit >= TrailingStopActivationPips)
         {
            double newSL = NormalizeDouble(markPrice + adaptiveTrailPips * pip, digits);
            if(currSL == 0.0 || newSL < currSL - point * 2)
               g_trade.PositionModify(ticket, newSL, currTP);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Route signal generation according to detected regime             |
//+------------------------------------------------------------------+
void CheckEntrySignals()
{
   if(HasOpenPosition()) return;
