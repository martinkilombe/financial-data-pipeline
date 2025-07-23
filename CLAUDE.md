# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python application for collecting and storing stock market data using Polygon.io and Yahoo Finance APIs. The project uses SQLAlchemy for database management and supports both SQLite and PostgreSQL.

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export POLYGON_API_KEY=your_key_here
```

### Running the Application

```bash
# Fetch historical data from Polygon.io
python main.py AAPL --days 30 --interval minute

# Fetch current data from Yahoo Finance
python yfinance_fetcher.py AAPL MSFT GOOGL

# Export SQLite to PostgreSQL
python sqlite_to_postgres.py -o stocks_export.sql

# Monitor stocks every minute (debug)
./debug_monitor.sh
```

### Testing and Linting
```bash
# Currently no test framework is set up
# No linting configuration exists yet
```

## Architecture

### Core Components

1. **main.py** - Polygon.io historical data fetcher
   - Uses Click for CLI interface
   - Fetches minute/hour/day aggregated bars
   - Saves to database with batch commits
   - Supports configurable time ranges

2. **yfinance_fetcher.py** - Yahoo Finance current data fetcher
   - Fetches near real-time stock prices
   - Supports multiple tickers in one run
   - Designed for cron/scheduler execution

3. **sqlite_to_postgres.py** - Database export utility
   - Exports SQLite data to PostgreSQL INSERT statements
   - Supports filtering and batching
   - Generates complete SQL with table creation

4. **database.py** - SQLAlchemy models
   - Stock model with ticker, time, OHLC data
   - JSON metadata field for additional data
   - Session management

5. **settings.py** - Configuration management
   - DATABASE_URL (supports SQLite/PostgreSQL)
   - API keys and default values
   - Centralized configuration

### Database Schema

```sql
stocks table:
- id: Primary key (auto-increment)
- ticker: Stock symbol (indexed)
- time: Unix timestamp (indexed)
- high, low, avg, sale: Price data (float)
- meta: JSON field for volume, transactions, etc.
```

### API Integration

- **Polygon.io**: Historical data with 5 req/min limit on free tier
- **Yahoo Finance**: Near real-time data via yfinance library
- Both save to the same database schema

## Important Notes

- Always activate virtual environment before running
- Check API rate limits (Polygon: 5/min, Yahoo: ~200-300/day)
- Use batch commits for large data imports
- The meta JSON field stores source-specific data
- Database URL can be overridden via environment variable