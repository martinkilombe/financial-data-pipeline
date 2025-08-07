#!/bin/bash

# Debug script to monitor AAPL every minute
# Press Ctrl+C to stop

echo "Starting AAPL monitor - fetching every 60 seconds"
echo "Press Ctrl+C to stop"
echo "----------------------------------------"

while true; do
    # Wait until next minute mark + 5 second buffer
    current_second=$(date +%S)
    sleep_time=$((60 - current_second + 5))
    sleep $sleep_time
    
    # Get current time
    echo -n "$(date '+%Y-%m-%d %H:%M:%S') - "
    
    # Run the fetcher (ensure we're in the correct directory and use venv)
    cd "$(dirname "${BASH_SOURCE[0]}")" && ./venv/bin/python3 yfinance_fetcher.py AAPL AIQ AMD AMZN AVGO GOOGL INTC META MSFT NVDA ORCL PLTR TSM
done