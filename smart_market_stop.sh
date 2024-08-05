#!/bin/bash

# Smart Market Stop Script
# Gracefully stops the debug_monitor.sh process

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/market_monitor.log"
MONITOR_PID_FILE="$SCRIPT_DIR/monitor.pid"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [STOP] $1" >> "$LOG_FILE"
}

log_message "Starting market stop procedure..."

# Function to kill process and its children
kill_process_tree() {
    local pid=$1
    local signal=${2:-TERM}
    
    # Kill child processes first
    local children=$(pgrep -P "$pid" 2>/dev/null)
    for child in $children; do
        log_message "Killing child process $child"
        kill -$signal "$child" 2>/dev/null
    done
    
    # Kill the main process
    log_message "Killing main process $pid with signal $signal"
    kill -$signal "$pid" 2>/dev/null
}

# Check if PID file exists
if [ -f "$MONITOR_PID_FILE" ]; then
    MONITOR_PID=$(cat "$MONITOR_PID_FILE")
    log_message "Found PID file with PID: $MONITOR_PID"
    
    # Check if process is actually running
    if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
        log_message "Process $MONITOR_PID is running, attempting graceful shutdown..."
        
        # Try graceful shutdown first (TERM signal)
        kill_process_tree "$MONITOR_PID" "TERM"
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! ps -p "$MONITOR_PID" > /dev/null 2>&1; then
                log_message "Process $MONITOR_PID terminated gracefully after ${i} seconds"
                break
            fi
            sleep 1
        done
        
        # If still running, force kill
        if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
            log_message "Process $MONITOR_PID still running, forcing shutdown..."
            kill_process_tree "$MONITOR_PID" "KILL"
            sleep 2
            
            if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
                log_message "ERROR: Could not kill process $MONITOR_PID"
                exit 1
            else
                log_message "Process $MONITOR_PID force-killed successfully"
            fi
        fi
    else
        log_message "Process $MONITOR_PID not running (stale PID file)"
    fi
    
    # Remove PID file
    rm -f "$MONITOR_PID_FILE"
    log_message "Removed PID file"
else
    log_message "No PID file found"
fi

# Backup: kill any remaining debug_monitor.sh processes
REMAINING_PIDS=$(pgrep -f "debug_monitor.sh" 2>/dev/null)
if [ -n "$REMAINING_PIDS" ]; then
    log_message "Found additional debug_monitor.sh processes: $REMAINING_PIDS"
    for pid in $REMAINING_PIDS; do
        log_message "Killing remaining process $pid"
        kill_process_tree "$pid" "TERM"
        sleep 2
        if ps -p "$pid" > /dev/null 2>&1; then
            kill_process_tree "$pid" "KILL"
        fi
    done
fi

# Final verification
FINAL_CHECK=$(pgrep -f "debug_monitor.sh" 2>/dev/null)
if [ -n "$FINAL_CHECK" ]; then
    log_message "WARNING: Some debug_monitor.sh processes may still be running: $FINAL_CHECK"
    exit 1
else
    log_message "All debug_monitor.sh processes stopped successfully"
    exit 0
fi