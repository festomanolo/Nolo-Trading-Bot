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
