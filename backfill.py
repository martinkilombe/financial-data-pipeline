import os
import sys
from datetime import datetime, timedelta

import click
from loguru import logger
from polygon import RESTClient

from database import Stock, get_session


@click.command()
@click.argument("ticker")
@click.option("--days", default=90, help="Number of days to fetch (default: 90)")
@click.option("--interval", default="minute", help="Time interval: minute, hour, day (default: minute)")
@click.option("--multiplier", default=1, help="Multiplier for interval (default: 1)")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(ticker, days, interval, multiplier, debug):
    """Fetch stock data for TICKER and save to database."""
    # Configure logging
    logger.remove()  # Remove default handler
    if debug:
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    else:
        logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    
    logger.info(f"Starting data fetch for {ticker}")
    logger.debug(f"Parameters: days={days}, interval={interval}, multiplier={multiplier}")
    
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        logger.error("POLYGON_API_KEY environment variable not set")
        return

    logger.debug("Initializing Polygon client and database session")
    client = RESTClient(api_key=api_key)
    session = get_session()

    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    logger.info(f"Fetching {multiplier} {interval} data from {from_date.date()} to {to_date.date()}")

    try:
        count = 0
        logger.debug(f"Starting API request to Polygon for {ticker}")
        
        for agg in client.list_aggs(
            ticker=ticker,
            multiplier=multiplier,
            timespan=interval,
            from_=from_date.strftime("%Y-%m-%d"),
            to=to_date.strftime("%Y-%m-%d"),
            limit=50000,
        ):
            # Create Stock record
            timestamp = int(agg.timestamp / 1000)
            avg_price = agg.vwap if hasattr(agg, 'vwap') and agg.vwap else (agg.high + agg.low) / 2
            
            logger.debug(f"Processing bar: time={datetime.fromtimestamp(timestamp)}, "
                        f"OHLC={agg.open}/{agg.high}/{agg.low}/{agg.close}, "
                        f"volume={agg.volume}")
            
            stock = Stock(
                ticker=ticker,
                time=timestamp,
                high=agg.high,
                low=agg.low,
                avg=avg_price,
                sale=agg.close,
                meta={
                    "open": agg.open,
                    "volume": agg.volume,
                    "transactions": agg.transactions if hasattr(agg, 'transactions') else None,
                    "vwap": agg.vwap if hasattr(agg, 'vwap') else None,
                }
            )
            session.add(stock)
            count += 1

            # Commit in batches
            if count % 1000 == 0:
                session.commit()
                logger.info(f"Saved {count} records...")
                logger.debug("Batch committed to database")

        # Final commit
        session.commit()
        logger.success(f"Successfully saved {count} records for {ticker}")
        
        if count == 0:
            logger.warning("No data was returned from the API")

    except Exception as e:
        session.rollback()
        logger.error(f"Error occurred: {type(e).__name__}: {e}")
        logger.debug("Database transaction rolled back")
        raise
    finally:
        session.close()
        logger.debug("Database session closed")


if __name__ == "__main__":
    main()