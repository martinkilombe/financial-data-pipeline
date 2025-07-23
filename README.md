# Stonks - Stock Market Data Collector

A Python application for collecting and storing stock market data using Polygon.io and Yahoo Finance APIs.

## Features

- Fetch historical stock data from Polygon.io (minute, hour, day intervals)
- Fetch near real-time stock data from Yahoo Finance
- Store data in SQLite database (configurable)
- Command-line interface with detailed logging
- Support for multiple tickers
- Automatic batch processing for large datasets

## Prerequisites

- Python 3.12+
- Polygon.io API key (free tier available)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
cd /Users/jimbee/projects/stonks
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "POLYGON_API_KEY=your_polygon_api_key_here" > .env

# Or export directly
export POLYGON_API_KEY=your_polygon_api_key_here
```

5. Initialize database (if using Alembic):
```bash
alembic upgrade head
```

## Usage

### Fetch Historical Data (Polygon.io)

Fetch historical stock data with configurable time ranges and intervals:

```bash
# Fetch 90 days of minute data for AAPL (default)
python main.py AAPL

# Fetch 30 days of minute data
python main.py AAPL --days 30

# Fetch hourly data
python main.py AAPL --interval hour

# Fetch daily data with 5-day bars
python main.py AAPL --interval day --multiplier 5

# Enable debug logging
python main.py AAPL --debug
```

### Fetch Current Data (Yahoo Finance)

Get current/near real-time stock prices:

```bash
# Single ticker
python yfinance_fetcher.py AAPL

# Multiple tickers
python yfinance_fetcher.py AAPL MSFT GOOGL TSLA

# With debug logging
python yfinance_fetcher.py AAPL --debug
```

### Automated Monitoring

Use the debug monitor script to fetch data every minute:

```bash
# Make script executable (first time only)
chmod +x debug_monitor.sh

# Run monitor
./debug_monitor.sh
```

### Scheduling with Cron

To automatically fetch data every minute during market hours:

```bash
# Edit crontab
crontab -e

# Add this line (runs every minute, Monday-Friday, 9:30 AM - 4:00 PM EST)
* 9-16 * * 1-5 cd /Users/jimbee/projects/stonks && source venv/bin/activate && python yfinance_fetcher.py AAPL MSFT GOOGL
```

### Export to PostgreSQL

Export SQLite data to PostgreSQL-compatible SQL file:

```bash
# Export all data
python sqlite_to_postgres.py

# Export to custom filename
python sqlite_to_postgres.py -o stocks_export.sql

# Export specific ticker only
python sqlite_to_postgres.py --where "ticker='AAPL'"

# Export with custom batch size
python sqlite_to_postgres.py --batch-size 500

# Import to PostgreSQL
psql -U username -d database -f stocks_dump.sql
```

## Database Schema

The application uses a single `stocks` table with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| ticker | String(10) | Stock symbol (indexed) |
| time | Integer | Unix timestamp (indexed) |
| high | Float | Highest price in period |
| low | Float | Lowest price in period |
| avg | Float | Average price (VWAP or calculated) |
| sale | Float | Closing/current price |
| meta | JSON | Additional data (volume, open, etc.) |

## Configuration

Settings can be modified in `settings.py`:

- `DATABASE_URL`: Database connection string (default: `sqlite:///stocks.db`)
- `DEFAULT_DAYS`: Default number of days to fetch (90)
- `DEFAULT_INTERVAL`: Default time interval ("minute")
- `BATCH_COMMIT_SIZE`: Records per database commit (1000)

### Using Different Database

```bash
# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/stocks"

# MySQL
export DATABASE_URL="mysql://user:password@localhost/stocks"
```

## API Limitations

### Polygon.io (Free Tier)
- 5 API calls per minute
- 2 years of historical data
- End-of-day data (real-time requires paid plan)
- No WebSocket access

### Yahoo Finance (yfinance)
- No official rate limits but ~200-300 requests/day
- Real-time for major stocks, delayed for others
- Data accuracy varies by ticker

## Troubleshooting

### Common Issues

1. **"POLYGON_API_KEY environment variable not set"**
   ```bash
   export POLYGON_API_KEY=your_key_here
   # Or add to .env file
   ```

2. **"No data was returned from the API"**
   - Check if market is open
   - Verify ticker symbol is correct
   - Ensure API key is valid

3. **Database errors**
   ```bash
   # Reset database
   rm stocks.db
   python -c "from database import Base, engine; Base.metadata.create_all(engine)"
   ```

4. **Module not found errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## Development

### Project Structure
```
stonks/
├── main.py                 # Polygon.io historical data fetcher
├── yfinance_fetcher.py     # Yahoo Finance current data fetcher
├── sqlite_to_postgres.py   # SQLite to PostgreSQL export script
├── database.py             # SQLAlchemy models and database setup
├── settings.py             # Configuration settings
├── debug_monitor.sh        # Debug monitoring script
├── requirements.txt        # Python dependencies
├── alembic/               # Database migrations
├── alembic.ini            # Alembic configuration
├── .env                   # Environment variables (not in git)
└── stocks.db              # SQLite database (created automatically)
```

### Adding New Features

1. Always use virtual environment
2. Follow existing code patterns
3. Add appropriate logging
4. Update requirements.txt if adding dependencies
5. Test with small date ranges first

## License

This project is for educational and personal use only. Ensure compliance with API terms of service.