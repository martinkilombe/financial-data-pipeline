# Market Hours Cron Setup

This guide shows how to set up automatic market hours monitoring on your VPS using the smart start/stop scripts.

## Prerequisites

1. Install the new dependency:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

2. Make scripts executable:
```bash
chmod +x smart_market_start.sh
chmod +x smart_market_stop.sh
chmod +x debug_monitor.sh
```

## Cron Configuration

### For VPS in UTC timezone:

Add these lines to your crontab (`crontab -e`):

```bash
# Start monitoring at 9:25 AM ET (allow 5 min buffer before market open)
# UTC times: 14:25 (EST) or 13:25 (EDT)
25 13 * * 1-5 /full/path/to/stonks/smart_market_start.sh
25 14 * * 1-5 /full/path/to/stonks/smart_market_start.sh

# Stop monitoring at 4:05 PM ET (5 min after market close)
# UTC times: 21:05 (EST) or 20:05 (EDT)
05 20 * * 1-5 /full/path/to/stonks/smart_market_stop.sh
05 21 * * 1-5 /full/path/to/stonks/smart_market_stop.sh
```

### For VPS in Eastern timezone:

```bash
# Start monitoring at 9:25 AM ET
25 9 * * 1-5 /full/path/to/stonks/smart_market_start.sh

# Stop monitoring at 4:05 PM ET  
05 16 * * 1-5 /full/path/to/stonks/smart_market_stop.sh
```

## How It Works

1. **Start Script** (`smart_market_start.sh`):
   - Runs at 9:25 AM ET to allow 5-minute buffer before market open
   - Checks if market is actually open (handles holidays automatically)
   - Only starts `debug_monitor.sh` if market is open and not already running
   - Logs all decisions to `market_monitor.log`

2. **Stop Script** (`smart_market_stop.sh`):
   - Runs at 4:05 PM ET (5 minutes after market close)
   - Gracefully stops `debug_monitor.sh` and any child processes
   - Logs shutdown process

3. **Market Check** (`market_check.py`):
   - Uses `pandas_market_calendars` library for accurate NYSE calendar
   - Automatically handles holidays, early closes, weekends
   - Converts timezones automatically (EST/EDT)

## Testing

Test the setup before deploying:

```bash
# Test market status check
python3 market_check.py status

# Test if should start monitoring  
python3 market_check.py should_start

# Test start script (won't start if market closed)
./smart_market_start.sh

# Test stop script
./smart_market_stop.sh

# Check logs
tail -f market_monitor.log
```

## Monitoring

- **Logs**: Check `market_monitor.log` for all start/stop decisions
- **Process**: Use `ps aux | grep debug_monitor` to see if running
- **PID file**: `monitor.pid` contains the current process ID when running

## Troubleshooting

1. **Scripts not running**: Check cron logs (`/var/log/cron` or `journalctl -u cron`)
2. **Market check failing**: Ensure `pandas_market_calendars` is installed in venv
3. **Permission errors**: Ensure all scripts are executable
4. **Timezone issues**: The scripts handle timezone conversion automatically

## Benefits

- **Automatic**: Runs without intervention
- **Holiday-aware**: Won't run on market holidays
- **Timezone-safe**: Handles EST/EDT transitions
- **Crash-resistant**: Each cron execution is independent
- **Logged**: Full audit trail of start/stop decisions