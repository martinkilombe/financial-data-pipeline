#!/bin/bash

# Smart Market Start Script
# Checks if market is open and starts debug_monitor.sh if appropriate

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
LOG_FILE="$SCRIPT_DIR/market_monitor.log"
MONITOR_SCRIPT="$SCRIPT_DIR/debug_monitor.sh"
PYTHON_VENV="$SCRIPT_DIR/venv/bin/python3"
MARKET_CHECK="$SCRIPT_DIR/market_check.py"
MONITOR_PID_FILE="$SCRIPT_DIR/monitor.pid"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [START] $1" >> "$LOG_FILE"
}

# Check if Python virtual environment exists
if [ ! -f "$PYTHON_VENV" ]; then
    log_message "ERROR: Python virtual environment not found at $PYTHON_VENV"
    exit 1
fi

# Check if market_check.py exists
if [ ! -f "$MARKET_CHECK" ]; then
    log_message "ERROR: market_check.py not found at $MARKET_CHECK"
    exit 1
fi

# Check if debug_monitor.sh exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    log_message "ERROR: debug_monitor.sh not found at $MONITOR_SCRIPT"
    exit 1
fi

# Make sure debug_monitor.sh is executable
chmod +x "$MONITOR_SCRIPT"

log_message "Starting market check..."

# Check if we should start monitoring
if $PYTHON_VENV "$MARKET_CHECK" should_start; then
    # Get the market status for logging
    MARKET_STATUS=$($PYTHON_VENV "$MARKET_CHECK" should_start 2>&1)
    log_message "Market check passed: $MARKET_STATUS"
    
    # Check if monitor is already running
    if [ -f "$MONITOR_PID_FILE" ]; then
        EXISTING_PID=$(cat "$MONITOR_PID_FILE")
        if ps -p "$EXISTING_PID" > /dev/null 2>&1; then
            log_message "Monitor already running with PID $EXISTING_PID, skipping start"
            exit 0
        else
            log_message "Stale PID file found, removing..."
            rm -f "$MONITOR_PID_FILE"
        fi
    fi
    
    # Check if debug_monitor.sh is already running (backup check)
    if pgrep -f "debug_monitor.sh" > /dev/null; then
        EXISTING_PID=$(pgrep -f "debug_monitor.sh")
        log_message "Monitor already running with PID $EXISTING_PID (found via pgrep), skipping start"
        echo "$EXISTING_PID" > "$MONITOR_PID_FILE"
        exit 0
    fi
    
    # Start the monitor
    log_message "Starting debug_monitor.sh..."
    
    # Start debug_monitor.sh in background and capture its PID
    nohup "$MONITOR_SCRIPT" >> "$LOG_FILE" 2>&1 &
    MONITOR_PID=$!
    
    # Save PID to file
    echo "$MONITOR_PID" > "$MONITOR_PID_FILE"
    
    # Give it a moment to start
    sleep 2
    
    # Verify it's still running
    if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
        log_message "Successfully started monitor with PID $MONITOR_PID"
        exit 0
    else
        log_message "ERROR: Failed to start monitor (PID $MONITOR_PID not running)"
        rm -f "$MONITOR_PID_FILE"
        exit 1
    fi
    
else
    # Get the reason why we shouldn't start
    MARKET_STATUS=$($PYTHON_VENV "$MARKET_CHECK" should_start 2>&1)
    log_message "Market check failed, not starting: $MARKET_STATUS"
    exit 1
fi