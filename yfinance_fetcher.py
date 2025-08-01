import sys
import time
from datetime import datetime

import click
import yfinance as yf
from loguru import logger

from database import Stock, get_session


@click.command()
@click.argument("tickers", nargs=-1, required=True)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(tickers, debug):
    """Fetch current stock data for one or more TICKERS and save to database.
    
    Examples:
        python yfinance_fetcher.py AAPL
        python yfinance_fetcher.py AAPL MSFT GOOGL
    """
    # Configure logging
    logger.remove()
    if debug:
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    else:
        logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    
    logger.info(f"Fetching data for {len(tickers)} ticker(s): {', '.join(tickers)}")
    
    session = get_session()
    current_time = int(time.time())
    
    try:
        for ticker_symbol in tickers:
            logger.debug(f"Processing {ticker_symbol}")
            
            try:
                # Create ticker object
                ticker = yf.Ticker(ticker_symbol)
                
                # Get current info
                info = ticker.info
                
                # Get 1-minute data for prices and volume
                logger.debug(f"Fetching 1-minute data")
                minute_data = ticker.history(period="1d", interval="1m", prepost=True)
                
                if minute_data.empty:
                    logger.warning(f"No 1-minute data available for {ticker_symbol}")
                    continue
                
                # Get current price from latest 1-minute bar
                current_price = float(minute_data['Close'].iloc[-1])
                
                # Calculate high/low/avg for today from 1-minute data
                high = minute_data['High'].max()
                low = minute_data['Low'].min()
                avg = (high + low) / 2
                
                # Get volume directly from 1-minute data
                # Use previous minute if current minute has 0 volume (data lag)
                current_volume = int(minute_data['Volume'].iloc[-1])
                if current_volume == 0 and len(minute_data) > 1:
                    volume = int(minute_data['Volume'].iloc[-2])
                    logger.debug(f"Using previous minute volume (current=0): {volume:,}")
                else:
                    volume = current_volume
                    logger.debug(f"Using current minute volume: {volume:,}")
                
                # Get the most recent data point from 1-minute data
                latest_row = minute_data.iloc[-1]
                
                logger.info(f"{ticker_symbol}: Price=${current_price:.2f}, "
                           f"High=${high:.2f}, Low=${low:.2f}, Volume={volume:,}")
                
                # Create Stock record
                stock = Stock(
                    ticker=ticker_symbol,
                    time=current_time,
                    high=float(high),
                    low=float(low),
                    avg=float(avg),
                    sale=float(current_price),
                    meta={
                        "source": "yfinance",
                        "volume": int(volume),
                        "open": float(latest_row['Open']),
                        "close": float(latest_row['Close']),
                        "day_high": float(info.get('dayHigh', high)),
                        "day_low": float(info.get('dayLow', low)),
                        "previous_close": float(info.get('previousClose', 0)),
                        "market_cap": info.get('marketCap'),
                        "pe_ratio": info.get('trailingPE'),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                session.add(stock)
                logger.debug(f"Added {ticker_symbol} to session")
                
            except Exception as e:
                logger.error(f"Error processing {ticker_symbol}: {type(e).__name__}: {e}")
                continue
        
        # Commit all records
        session.commit()
        logger.success(f"Successfully saved data for {len(tickers)} ticker(s)")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {type(e).__name__}: {e}")
        raise
    finally:
        session.close()
        logger.debug("Database session closed")


if __name__ == "__main__":
    main()