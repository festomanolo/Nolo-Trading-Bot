//+------------------------------------------------------------------+
//| Advanced Adaptive Trading Bot - Multi-Strategy System v4.0       |
//| Combines machine learning prediction, Kalman state estimation,   |
//| Hurst regime detection, Smart Money Concepts, and Bayesian Kelly |
//+------------------------------------------------------------------+
#property strict
#property copyright   "Market Expert 2025 - Nolo Quantitative Systems"
#property link        "https://github.com/festomanolo/Nolo-Trading-Bot"
#property version     "4.0"
#property description "Next-Level Multi-Timeframe Adaptive Forex Trading Strategy with Kalman Filter, Hurst Exponent, Smart Money Concepts & Online Neural Scorer"

// Enumerations for strategy flexibility
enum REGIME_TYPE 
{
   TREND_FOLLOWING,    // Trend Following Mode (Kalman + SuperTrend + Ichimoku)
   RANGE_TRADING,      // Range / Ornstein-Uhlenbeck Mean Reversion Mode
   BREAKOUT,           // Institutional Breakout & SMC Mode
   VOLATILITY,         // Volatility Squeeze & Momentum Mode
   SMC_INSTITUTIONAL,  // Smart Money Concepts (Order Block / FVG / Sweep)
   ADAPTIVE            // Auto-detect Regime (Bayesian + Hurst + ADX + Kalman)
};

enum RISK_MODEL 
{
   FIXED,              // Fixed Risk %
   KELLY,              // Classic Kelly Criterion
   ADAPTIVE_KELLY,     // Streak-Adjusted Adaptive Kelly
   BAYESIAN_KELLY,     // Bayesian Beta-Posterior + Neural Probability Kelly
   ANTI_MARTINGALE     // Anti-Martingale (increase size after wins)
};

// Input Parameters - Strategy Selection & Intelligence
input REGIME_TYPE MarketRegimeMode           = ADAPTIVE;        // Market Regime Detection Method
input RISK_MODEL  RiskModelType              = BAYESIAN_KELLY;  // Risk Management Method
input bool        UseVolatilityFilter        = true;            // Filter trades during extreme volatility
input bool        UsePriceMomentum           = true;            // Use Kalman & OrderFlow momentum confirmation
input bool        UseMarketStructure         = true;            // Use SMC market structure (S/R, OB, FVG)
input bool        UseAlternateTimeframes     = true;            // Use multi-timeframe confirmation
input bool        UseSmartTrailingStop       = true;            // Enable volatility-adaptive trailing stop
input bool        UseNeuralSignalFilter      = true;            // Enable Online Neural Perceptron Scorer
input bool        UseMacroNewsFilter         = true;            // Enable High-Impact News & Rollover Guard
input bool        ShowTelemetryHUD           = true;            // Show On-Chart Institutional Telemetry HUD

// Input Parameters - Moving Averages
input ENUM_TIMEFRAMES MainTimeframe          = PERIOD_M5;       // Main trading timeframe
input ENUM_TIMEFRAMES HigherTimeframe        = PERIOD_H1;       // Higher confirmation timeframe
input int         FastMAPeriod               = 8;               // Fast MA period (optimized)
input int         SlowMAPeriod               = 21;              // Slow MA period
input ENUM_MA_METHOD FastMAMethod            = MODE_EMA;        // Fast MA method
input ENUM_MA_METHOD SlowMAMethod            = MODE_EMA;        // Slow MA method

// Input Parameters - Oscillators
input int         RSIPeriod                  = 14;              // RSI period
input int         RSI_UpperLevel             = 70;              // RSI upper threshold
input int         RSI_LowerLevel             = 30;              // RSI lower threshold
input int         StochasticKPeriod          = 5;               // Stochastic %K period
input int         StochasticDPeriod          = 3;               // Stochastic %D period
input int         StochasticSlowing          = 3;               // Stochastic slowing

// Input Parameters - MACD
input int         MACD_FastEMA               = 12;              // MACD Fast EMA
input int         MACD_SlowEMA               = 26;              // MACD Slow EMA
input int         MACD_SignalSMA             = 9;               // MACD Signal SMA

// Input Parameters - Bollinger & ATR
input int         BollingerPeriod            = 20;              // Bollinger Bands period
input double      BollingerDeviation         = 2.0;             // Bollinger Bands deviation
input int         ATRPeriod                  = 14;              // ATR period for volatility

// Input Parameters - SuperTrend & Ichimoku
input double      SuperTrendMultiplier       = 2.5;             // SuperTrend multiplier (optimized)
input int         TenkanSen                  = 9;               // Ichimoku Tenkan-sen period
input int         KijunSen                   = 26;              // Ichimoku Kijun-sen period
input int         SenkouSpanB                = 52;              // Ichimoku Senkou Span B period

// Input Parameters - Advanced Risk Management
input double      MaxRisk                    = 1.0;             // Maximum risk per trade (%)
input double      AdaptiveRiskMultiplier     = 1.4;             // Risk multiplier for strong signals
input double      ATRMultiplier              = 2.0;             // ATR multiplier for stop loss
input double      Slippage                   = 3.0;             // Maximum slippage allowed
input int         MaxDrawdown                = 5;               // Max daily drawdown %
input double      MaxTotalDrawdown           = 9.0;             // Max overall trailing drawdown %
input double      KellyFactor                = 0.35;            // Kelly factor (conservative)
input int         MaxDailyTrades             = 6;               // Maximum trades per day
input int         MinBarsSinceLastTrade      = 3;               // Minimum bars between trades
input int         MaxSpread                  = 20;              // Maximum allowed spread in points
input double      MinNeuralWinProbability    = 0.54;            // Minimum Neural Scorer win probability

// Input Parameters - Smart Exits
input double      RiskRewardRatio            = 2.2;             // Risk-to-reward ratio
input bool        UseBreakEven               = true;            // Use break-even stop
input double      BreakEvenTriggerPips       = 14.0;            // Pips needed to move SL to entry
input double      BreakEvenPlusPips          = 2.0;             // Additional pips for break-even
input double      TrailingStopActivationPips = 20.0;            // Pips to activate trailing stop
input double      TrailingStopDistance       = 12.0;            // Trailing stop distance in pips

// Global indicator & state buffers
#define BUFFER_SIZE 100
double FastMA[], SlowMA[], RSIValue[], MACDMain[], MACDSignal[], UpperBB[], LowerBB[], ATRValue[];
double SuperTrendValue[], SuperTrendDirection[], StochMain[], StochSignal[];
double IchimokuTenkan[], IchimokuKijun[], IchimokuSenkouA[], IchimokuSenkouB[];

// State-space Kalman Filter & Fractal Regime telemetry
double KalmanLevel = 0.0;
double KalmanVelocity = 0.0;
double CurrentHurstExponent = 0.50;
double CurrentEfficiencyRatio = 0.40;
double CurrentOrderFlowBuyRatio = 0.50;
double LastNeuralWinProb = 0.60;

// Risk & Performance Tracking
double AccountStartBalance;
double AccountHighWaterMark;
int    CurrentSessionDay = -1;
datetime LastTradeTime;
int    TotalTradesThisSession = 0;
int    ConsecutiveLosses = 0;
int    ConsecutiveWins = 0;
double WinRate = 0.58;
double BetaAlpha = 6.0;
double BetaBeta  = 4.0;
int    TotalTrades = 0;
int    WinningTrades = 0;
string CurrentMarketRegime = "UNKNOWN";
int    Magic = 123456;

// Online Neural Scorer weights
double W_Trend = 0.55, W_Kalman = 0.42, W_Hurst = 0.35, W_ADX = 0.28, W_SMC = 0.48, W_OFlow = 0.40, W_HTF = 0.50, W_Bias = -0.15;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   ArrayResize(FastMA, BUFFER_SIZE);
   ArrayResize(SlowMA, BUFFER_SIZE);
   ArrayResize(RSIValue, BUFFER_SIZE);
   ArrayResize(MACDMain, BUFFER_SIZE);
   ArrayResize(MACDSignal, BUFFER_SIZE);
   ArrayResize(UpperBB, BUFFER_SIZE);
   ArrayResize(LowerBB, BUFFER_SIZE);
   ArrayResize(ATRValue, BUFFER_SIZE);
   ArrayResize(SuperTrendValue, BUFFER_SIZE);
   ArrayResize(SuperTrendDirection, BUFFER_SIZE);
   ArrayResize(StochMain, BUFFER_SIZE);
   ArrayResize(StochSignal, BUFFER_SIZE);
   ArrayResize(IchimokuTenkan, BUFFER_SIZE);
   ArrayResize(IchimokuKijun, BUFFER_SIZE);
   ArrayResize(IchimokuSenkouA, BUFFER_SIZE);
   ArrayResize(IchimokuSenkouB, BUFFER_SIZE);

   AccountStartBalance  = AccountBalance();
   AccountHighWaterMark = AccountStartBalance;

   if(FastMAPeriod >= SlowMAPeriod)
   {
      Print("Error: Fast MA period must be less than Slow MA period");
      return INIT_PARAMETERS_INCORRECT;
   }

   Print("Nolo Trading Bot v4.0 initialized with Kalman + Hurst + SMC + Neural Strategy System");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Comment("");
   Print("Expert removed. Reason code: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   RefreshDailySessionCounters();

   if(MarketInfo(Symbol(), MODE_SPREAD) > MaxSpread)
      return;

   if(IsDailyDrawdownExceeded() || IsTotalDrawdownExceeded())
      return;

   UpdateIndicators();
   UpdateKalmanAndMicrostructure();
   DetectMarketRegime();
   ManageOpenTrades();
   RenderTelemetryHUD();

   if(TotalTradesThisSession >= MaxDailyTrades) return;
   if(BarsSinceLastTrade() < MinBarsSinceLastTrade) return;
   if(UseMacroNewsFilter && IsHighImpactNews()) return;

   CheckTradeEntrySignals();
}

//+------------------------------------------------------------------+
//| Reset daily counters and high-water mark at new session day      |
//+------------------------------------------------------------------+
void RefreshDailySessionCounters()
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   if(dt.day_of_year != CurrentSessionDay)
   {
      CurrentSessionDay      = dt.day_of_year;
      AccountStartBalance    = AccountBalance();
      TotalTradesThisSession = 0;
   }
   if(AccountEquity() > AccountHighWaterMark)
      AccountHighWaterMark = AccountEquity();
}

//+------------------------------------------------------------------+
//| Update all technical indicators (oldest-to-newest for SuperTrend)|
//+------------------------------------------------------------------+
void UpdateIndicators()
{
   for(int i = BUFFER_SIZE - 1; i >= 0; i--)
   {
      FastMA[i]     = iMA(Symbol(), MainTimeframe, FastMAPeriod, 0, FastMAMethod, PRICE_CLOSE, i);
      SlowMA[i]     = iMA(Symbol(), MainTimeframe, SlowMAPeriod, 0, SlowMAMethod, PRICE_CLOSE, i);
      RSIValue[i]   = iRSI(Symbol(), MainTimeframe, RSIPeriod, PRICE_CLOSE, i);
      MACDMain[i]   = iMACD(Symbol(), MainTimeframe, MACD_FastEMA, MACD_SlowEMA, MACD_SignalSMA, PRICE_CLOSE, MODE_MAIN, i);
      MACDSignal[i] = iMACD(Symbol(), MainTimeframe, MACD_FastEMA, MACD_SlowEMA, MACD_SignalSMA, PRICE_CLOSE, MODE_SIGNAL, i);
      UpperBB[i]    = iBands(Symbol(), MainTimeframe, BollingerPeriod, BollingerDeviation, 0, PRICE_CLOSE, MODE_UPPER, i);
      LowerBB[i]    = iBands(Symbol(), MainTimeframe, BollingerPeriod, BollingerDeviation, 0, PRICE_CLOSE, MODE_LOWER, i);
      ATRValue[i]   = iATR(Symbol(), MainTimeframe, ATRPeriod, i);

      CalculateSuperTrend(i);

      StochMain[i]       = iStochastic(Symbol(), MainTimeframe, StochasticKPeriod, StochasticDPeriod, StochasticSlowing, MODE_SMA, 0, MODE_MAIN, i);
      StochSignal[i]     = iStochastic(Symbol(), MainTimeframe, StochasticKPeriod, StochasticDPeriod, StochasticSlowing, MODE_SMA, 0, MODE_SIGNAL, i);
      IchimokuTenkan[i]  = iIchimoku(Symbol(), MainTimeframe, TenkanSen, KijunSen, SenkouSpanB, MODE_TENKANSEN, i);
      IchimokuKijun[i]   = iIchimoku(Symbol(), MainTimeframe, TenkanSen, KijunSen, SenkouSpanB, MODE_KIJUNSEN, i);
      IchimokuSenkouA[i] = iIchimoku(Symbol(), MainTimeframe, TenkanSen, KijunSen, SenkouSpanB, MODE_SENKOUSPANA, i);
      IchimokuSenkouB[i] = iIchimoku(Symbol(), MainTimeframe, TenkanSen, KijunSen, SenkouSpanB, MODE_SENKOUSPANB, i);
   }
}

//+------------------------------------------------------------------+
//| Ratcheting SuperTrend calculation (fixes band ratcheting bug)    |
//+------------------------------------------------------------------+
void CalculateSuperTrend(int index)
{
   double high      = High[index];
   double low       = Low[index];
   double close     = Close[index];
   double avg_price = (high + low) * 0.5;
   double atr       = ATRValue[index];

   double up_band   = avg_price + (SuperTrendMultiplier * atr);
   double down_band = avg_price - (SuperTrendMultiplier * atr);

   if(index == BUFFER_SIZE - 1)
   {
      SuperTrendValue[index]     = down_band;
      SuperTrendDirection[index] = 1;
      return;
   }

   double prev_st    = SuperTrendValue[index + 1];
   double prev_dir   = SuperTrendDirection[index + 1];
   double prev_close = Close[index + 1];

   if(prev_dir > 0)
   {
      if(prev_close >= prev_st && down_band < prev_st)
         down_band = prev_st;
      if(close < down_band)
      {
         SuperTrendDirection[index] = -1;
         SuperTrendValue[index]     = up_band;
      }
      else
      {
         SuperTrendDirection[index] = 1;
         SuperTrendValue[index]     = down_band;
      }
   }
   else
   {
      if(prev_close <= prev_st && up_band > prev_st)
         up_band = prev_st;
      if(close > up_band)
      {
         SuperTrendDirection[index] = 1;
         SuperTrendValue[index]     = down_band;
      }
      else
      {
         SuperTrendDirection[index] = -1;
         SuperTrendValue[index]     = up_band;
      }
   }
}

//+------------------------------------------------------------------+
//| State-Space Kalman Filter, Hurst Exponent & OrderFlow Pressure   |
//+------------------------------------------------------------------+
void UpdateKalmanAndMicrostructure()
{
   // 1. 2D Kinematic Kalman Filter pass over recent 30 bars
   double level = Close[30];
   double vel   = 0.0;
   double p00 = 0.01, p01 = 0.0, p10 = 0.0, p11 = 0.0001;
   double q = 0.0001, r = 0.01;

   for(int i = 29; i >= 0; i--)
   {
      double predLevel = level + vel;
      double p00p = p00 + p10 + p01 + p11 + q * 0.25;
      double p01p = p01 + p11 + q * 0.5;
      double p10p = p10 + p11 + q * 0.5;
      double p11p = p11 + q;

      double innov = Close[i] - predLevel;
      double s     = MathMax(1e-12, p00p + r);
      double k0    = p00p / s;
      double k1    = p10p / s;

      level = predLevel + k0 * innov;
      vel   = vel + k1 * innov;
      p00   = (1.0 - k0) * p00p;
      p01   = (1.0 - k0) * p01p;
      p10   = p10p - k1 * p00p;
      p11   = p11p - k1 * p01p;
   }
   KalmanLevel    = level;
   KalmanVelocity = vel / MathMax(1e-9, ATRValue[0]);

   // 2. Rescaled Range (R/S) Hurst Exponent over 50 bars
   int n = 48;
   double logRet[48];
   double sumRet = 0.0;
   for(int i = 0; i < n; i++)
   {
      logRet[i] = MathLog(MathMax(1e-9, Close[i]) / MathMax(1e-9, Close[i + 1]));
      sumRet += logRet[i];
   }
   double meanRet = sumRet / n;
   double cum = 0.0, maxC = -1e9, minC = 1e9, varS = 0.0;
   for(int i = 0; i < n; i++)
   {
      double c = logRet[i] - meanRet;
      cum += c;
      if(cum > maxC) maxC = cum;
      if(cum < minC) minC = cum;
      varS += c * c;
   }
   double stdS = MathSqrt(varS / n);
   if(stdS > 1e-12 && (maxC - minC) > 0.0)
      CurrentHurstExponent = MathMax(0.05, MathMin(0.95, MathLog((maxC - minC) / stdS) / MathLog((double)n)));
   else
      CurrentHurstExponent = 0.50;

   // 3. Kaufman Efficiency Ratio (14 bars)
   double netMove = MathAbs(Close[0] - Close[14]);
   double pathMove = 0.0;
   for(int i = 0; i < 14; i++)
      pathMove += MathAbs(Close[i] - Close[i + 1]);
   CurrentEfficiencyRatio = (pathMove > 1e-12) ? (netMove / pathMove) : 0.30;

   // 4. Order Flow Intrabar Buying Pressure
   double buyVol = 0.0, totVol = 0.0;
   for(int i = 0; i < 10; i++)
   {
      double rng  = High[i] - Low[i];
      double frac = (rng > 1e-12) ? ((Close[i] - Low[i]) / rng) : 0.50;
      double v    = (double)MathMax(1, Volume[i]);
      buyVol += v * frac;
      totVol += v;
   }
   CurrentOrderFlowBuyRatio = (totVol > 0.0) ? (buyVol / totVol) : 0.50;
}

//+------------------------------------------------------------------+
//| Multi-Factor Bayesian & Fractal Market Regime Detection          |
//+------------------------------------------------------------------+
void DetectMarketRegime()
{
   double currentATR = ATRValue[0];
   double avgATR = 0.0;
   for(int i = 0; i < 20; i++) avgATR += ATRValue[i];
   avgATR /= 20.0;

   double bbWidth      = (UpperBB[0] - LowerBB[0]) / MathMax(1e-9, Close[0]) * 100.0;
   bool   maAlignment  = FastMA[0] > SlowMA[0];
   double adxValue     = iADX(Symbol(), MainTimeframe, 14, PRICE_CLOSE, MODE_MAIN, 0);
   bool   hasRecentHH  = HasRecentHigherHigh(10);
   bool   hasRecentLL  = HasRecentLowerLow(10);

   if(adxValue > 24.0 && maAlignment && (CurrentHurstExponent >= 0.48 || CurrentEfficiencyRatio >= 0.30))
      CurrentMarketRegime = "TREND_UP";
   else if(adxValue > 24.0 && !maAlignment && (CurrentHurstExponent >= 0.48 || CurrentEfficiencyRatio >= 0.30))
      CurrentMarketRegime = "TREND_DOWN";
   else if(hasRecentHH && Close[0] > UpperBB[1] && currentATR > avgATR * 1.08)
      CurrentMarketRegime = "BREAKOUT_UP";
   else if(hasRecentLL && Close[0] < LowerBB[1] && currentATR > avgATR * 1.08)
      CurrentMarketRegime = "BREAKOUT_DOWN";
   else if(bbWidth > 2.5 && currentATR > avgATR * 1.45)
      CurrentMarketRegime = "VOLATILITY";
   else if(adxValue < 22.0 && (CurrentHurstExponent < 0.52 || CurrentEfficiencyRatio < 0.32))
      CurrentMarketRegime = "RANGE";
   else
      CurrentMarketRegime = "MIXED";
}

bool HasRecentHigherHigh(int bars)
{
   double previousHigh = High[1];
   for(int i = 2; i < bars; i++)
      if(previousHigh < High[i]) previousHigh = High[i];
   return High[0] > previousHigh;
}

bool HasRecentLowerLow(int bars)
{
   double previousLow = Low[1];
   for(int i = 2; i < bars; i++)
      if(previousLow > Low[i]) previousLow = Low[i];
   return Low[0] < previousLow;
}

bool IsDailyDrawdownExceeded()
{
   double currentLoss = AccountEquity() - AccountStartBalance;
   if(currentLoss < 0 && MathAbs(currentLoss / AccountStartBalance) * 100.0 >= MaxDrawdown)
      return true;
   return false;
}

bool IsTotalDrawdownExceeded()
{
   if(AccountHighWaterMark <= 0.0) return false;
   double ddPct = ((AccountHighWaterMark - AccountEquity()) / AccountHighWaterMark) * 100.0;
   return (ddPct >= MaxTotalDrawdown);
}

//+------------------------------------------------------------------+
//| Real-Time Macroeconomic News & Midnight Rollover Filter          |
//+------------------------------------------------------------------+
bool IsHighImpactNews()
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);

   // 1. Bank Rollover & Spread Widening Window (22:50 - 00:10)
   if((dt.hour == 22 && dt.min >= 50) || dt.hour == 23 || (dt.hour == 0 && dt.min <= 10))
      return true;

   // 2. US Non-Farm Payrolls (First Friday of Month 13:15 - 14:00 UTC)
   if(StringFind(Symbol(), "USD") >= 0 && dt.day_of_week == 5 && dt.day <= 7)
   {
      if(dt.hour == 13 && dt.min >= 15 && dt.min <= 59)
         return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| Smart Money Concepts: Fair Value Gap & Liquidity Sweep Detectors |
//+------------------------------------------------------------------+
bool HasBullishSMCConfluence()
{
   double fvgUp = Low[0] - High[2];
   bool isBullFVG = (fvgUp >= ATRValue[0] * 0.25 && Close[1] > Open[1]);
   double priorLow = FindRecentSwingLow(15);
   double rng = MathMax(1e-9, High[0] - Low[0]);
   double lowerWick = MathMin(Open[0], Close[0]) - Low[0];
   bool isSweep = (Low[0] < priorLow && Close[0] > priorLow && (lowerWick / rng) >= 0.45);
   return (isBullFVG || isSweep);
}

bool HasBearishSMCConfluence()
{
   double fvgDn = Low[2] - High[0];
   bool isBearFVG = (fvgDn >= ATRValue[0] * 0.25 && Close[1] < Open[1]);
   double priorHigh = FindRecentSwingHigh(15);
   double rng = MathMax(1e-9, High[0] - Low[0]);
   double upperWick = High[0] - MathMax(Open[0], Close[0]);
   bool isSweep = (High[0] > priorHigh && Close[0] < priorHigh && (upperWick / rng) >= 0.45);
   return (isBearFVG || isSweep);
}

//+------------------------------------------------------------------+
//| Online Neural Perceptron Signal Probability Scorer               |
//+------------------------------------------------------------------+
double PredictNeuralWinProbability(int orderType, double trendConf)
{
   double dirSign = (orderType == OP_BUY) ? 1.0 : -1.0;
   double fKalman = MathMax(-1.0, MathMin(1.0, dirSign * KalmanVelocity));
   double fHurst  = (CurrentHurstExponent - 0.5) * 2.0;
   double adxVal  = iADX(Symbol(), MainTimeframe, 14, PRICE_CLOSE, MODE_MAIN, 0);
   double fADX    = MathMin(1.0, adxVal / 50.0);
   double fSMC    = (orderType == OP_BUY && HasBullishSMCConfluence()) || (orderType == OP_SELL && HasBearishSMCConfluence()) ? 0.90 : 0.45;
   double fOFlow  = dirSign * (CurrentOrderFlowBuyRatio - 0.5) * 2.0;
   double fHTF    = 0.75;

   double z = W_Bias
            + W_Trend  * trendConf
            + W_Kalman * fKalman
            + W_Hurst  * fHurst
            + W_ADX    * fADX
            + W_SMC    * fSMC
            + W_OFlow  * fOFlow
            + W_HTF    * fHTF;

   double clamped = MathMax(-15.0, MathMin(15.0, z));
   double prob    = 1.0 / (1.0 + MathExp(-clamped));
   LastNeuralWinProb = MathMax(0.05, MathMin(0.95, prob));
   return LastNeuralWinProb;
}

int BarsSinceLastTrade()
{
   datetime lastTradeTime = 0;
   for(int i = OrdersHistoryTotal() - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY))
      {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == Magic)
         {
            if(OrderCloseTime() > lastTradeTime)
               lastTradeTime = OrderCloseTime();
         }
      }
   }
   if(lastTradeTime == 0) return 999;
   return iBarShift(Symbol(), MainTimeframe, lastTradeTime, false);
}

void ManageOpenTrades()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
