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
