#!/usr/bin/env python3
"""
Simple market status checker using pandas_market_calendars.
Handles NYSE calendar, holidays, early closes, and timezone conversion automatically.
"""

import sys
from datetime import datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal
from zoneinfo import ZoneInfo

def get_market_status():
    """
    Check if NYSE is currently open.
    Returns (is_open, reason, current_et_time)
    """
    # Get NYSE calendar
    nyse = mcal.get_calendar('NYSE')
    
    # Get current time in ET
    now_et = datetime.now(ZoneInfo("America/New_York"))
    today = now_et.date()
    
    # Get today's market schedule
    schedule = nyse.schedule(start_date=today, end_date=today)
    
    if schedule.empty:
        # Market is closed today (weekend or holiday)
        if now_et.weekday() >= 5:  # Weekend
            return False, f"Weekend ({now_et.strftime('%A')})", now_et
        else:
            return False, f"Market holiday", now_et
    
    # Get market open and close times for today
    market_open = schedule.iloc[0]['market_open'].tz_convert('America/New_York')
    market_close = schedule.iloc[0]['market_close'].tz_convert('America/New_York')
    
    # Check if we're in trading hours
    if now_et < market_open:
        return False, f"Before market open (opens at {market_open.strftime('%H:%M')} ET)", now_et
    elif now_et >= market_close:
        # Check if it was an early close
        if market_close.hour == 13:  # 1:00 PM close
            return False, f"After early close (closed at {market_close.strftime('%H:%M')} ET)", now_et
        else:
            return False, f"After market close (closed at {market_close.strftime('%H:%M')} ET)", now_et
    else:
        # Market is open
        if market_close.hour == 13:  # Early close day
            return True, f"Market open (early close at {market_close.strftime('%H:%M')} ET)", now_et
        else:
            return True, f"Market open (closes at {market_close.strftime('%H:%M')} ET)", now_et

def should_start_monitoring():
    """
    Check if we should start monitoring now.
    More permissive - allows starting 5 minutes before market open.
    Returns (should_start, reason, current_et_time)
    """
    # Get NYSE calendar
    nyse = mcal.get_calendar('NYSE')
    
    # Get current time in ET
    now_et = datetime.now(ZoneInfo("America/New_York"))
    today = now_et.date()
    
    # Get today's market schedule
    schedule = nyse.schedule(start_date=today, end_date=today)
    
    if schedule.empty:
        # Market is closed today
        if now_et.weekday() >= 5:  # Weekend
            return False, f"Weekend ({now_et.strftime('%A')})", now_et
        else:
            return False, f"Market holiday", now_et
    
    # Get market open and close times for today
    market_open = schedule.iloc[0]['market_open'].tz_convert('America/New_York')
    market_close = schedule.iloc[0]['market_close'].tz_convert('America/New_York')
    
    # Allow starting 5 minutes before market open
    start_time = market_open - timedelta(minutes=5)
    
    if now_et < start_time:
        return False, f"Too early (can start at {start_time.strftime('%H:%M')} ET)", now_et
    elif now_et >= market_close:
        return False, f"Too late (market closed at {market_close.strftime('%H:%M')} ET)", now_et
    else:
        return True, f"Good time to start monitoring", now_et

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python market_check.py [status|should_start]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "status":
            is_open, reason, current_time = get_market_status()
            print(f"Current ET: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Market open: {is_open}")
            print(f"Reason: {reason}")
            sys.exit(0 if is_open else 1)
            
        elif command == "should_start":
            should_start, reason, current_time = should_start_monitoring()
            print(f"Current ET: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Should start: {should_start}")
            print(f"Reason: {reason}")
            sys.exit(0 if should_start else 1)
            
        else:
            print("Invalid command. Use 'status' or 'should_start'")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error checking market status: {e}")
        # On error, assume we should NOT start (fail safe)
        sys.exit(1)