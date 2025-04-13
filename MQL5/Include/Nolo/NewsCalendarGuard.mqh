//+------------------------------------------------------------------+
//|                                            NewsCalendarGuard.mqh |
//|                        Nolo Trading Bot v4.0 - Institutional EA  |
//|      Real-Time Economic Calendar & Session Rollover Guard        |
//+------------------------------------------------------------------+
#property copyright "Nolo Quantitative Systems 2025"
#property strict

#ifndef NOLO_NEWS_CALENDAR_GUARD_MQH
#define NOLO_NEWS_CALENDAR_GUARD_MQH

class CNewsCalendarGuard
{
private:
   int m_preNewsMinutes;
   int m_postNewsMinutes;

public:
   CNewsCalendarGuard(int preMinutes = 30, int postMinutes = 30)
   {
      m_preNewsMinutes  = preMinutes;
      m_postNewsMinutes = postMinutes;
   }

   bool IsHighImpactNewsWindow(string symbol, datetime currentTime)
   {
      MqlDateTime dt;
      TimeToStruct(currentTime, dt);

      // 1. Protect against Midnight Rollover & Bank Settlement Spread Widening (22:50 - 00:10)
      if((dt.hour == 22 && dt.min >= 50) || dt.hour == 23 || (dt.hour == 0 && dt.min <= 10))
         return true;

      // 2. US Non-Farm Payrolls (First Friday of Month 13:15 - 14:00 Server/UTC)
      if(StringFind(symbol, "USD") >= 0 && dt.day_of_week == 5 && dt.day <= 7)
      {
         if(dt.hour == 13 && dt.min >= 15 && dt.min <= 59)
            return true;
      }

      // 3. Native MQL5 Economic Calendar Integration (when compiled on MT5 build >= 2000)
#ifdef __MQL5__
      MqlCalendarValue values[];
      datetime fromTime = currentTime - m_preNewsMinutes * 60;
      datetime toTime   = currentTime + m_postNewsMinutes * 60;
      string baseCcy    = StringSubstr(symbol, 0, 3);
      string quoteCcy   = StringSubstr(symbol, 3, 3);

      if(CalendarValueHistory(values, fromTime, toTime, NULL, baseCcy) > 0)
      {
         for(int i = 0; i < ArraySize(values); i++)
         {
            MqlCalendarEvent ev;
            if(CalendarEventById(values[i].event_id, ev))
            {
               if(ev.importance == CALENDAR_IMPORTANCE_HIGH)
                  return true;
            }
         }
      }
      if(CalendarValueHistory(values, fromTime, toTime, NULL, quoteCcy) > 0)
      {
         for(int i = 0; i < ArraySize(values); i++)
         {
            MqlCalendarEvent ev;
            if(CalendarEventById(values[i].event_id, ev))
            {
               if(ev.importance == CALENDAR_IMPORTANCE_HIGH)
                  return true;
            }
