#!/bin/bash

# Debug script to monitor AAPL every minute
# Press Ctrl+C to stop

echo "Starting AAPL monitor - fetching every 60 seconds"
echo "Press Ctrl+C to stop"
echo "----------------------------------------"

while true; do
    # Get current time
    echo -n "$(date '+%Y-%m-%d %H:%M:%S') - "
    
    # Run the fetcher
    python yfinance_fetcher.py NVDA AAPL MSFT GOOGL META PLTR
    
    # Wait 60 seconds
    sleep 60
done