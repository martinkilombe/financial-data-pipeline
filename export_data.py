import json
import sys
from datetime import datetime

import click
from loguru import logger
from sqlalchemy import create_engine, text

from database import Stock
from settings import DATABASE_URL


@click.command()
@click.option("--output", "-o", default="stocks_dump.sql", help="Output SQL file (default: stocks_dump.sql)")
@click.option("--table", default="stocks", help="Target table name (default: stocks)")
@click.option("--batch-size", default=1000, help="Number of records per INSERT statement (default: 1000)")
@click.option("--where", help="WHERE clause to filter records (e.g., \"ticker='AAPL'\")")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(output, table, batch_size, where, debug):
    """Export SQLite stock data to PostgreSQL INSERT statements."""
    
    # Configure logging
    logger.remove()
    if debug:
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    else:
        logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    
    logger.info(f"Starting export from SQLite to PostgreSQL format")
    logger.info(f"Output file: {output}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Build query
        query = f"SELECT * FROM stocks"
        if where:
            query += f" WHERE {where}"
            logger.info(f"Applying filter: WHERE {where}")
        query += " ORDER BY id"
        
        # Count total records
        count_query = f"SELECT COUNT(*) FROM stocks"
        if where:
            count_query += f" WHERE {where}"
        
        with engine.connect() as conn:
            total_count = conn.execute(text(count_query)).scalar()
            logger.info(f"Total records to export: {total_count:,}")
            
            if total_count == 0:
                logger.warning("No records found to export")
                return
            
            # Open output file
            with open(output, 'w') as f:
                # Write header
                f.write("-- PostgreSQL dump from SQLite stocks database\n")
                f.write(f"-- Generated at: {datetime.now().isoformat()}\n")
                f.write(f"-- Total records: {total_count:,}\n")
                f.write("-- \n")
                f.write("-- Usage: psql -U username -d database -f stocks_dump.sql\n")
                f.write("\n")
                
                # Write table creation (optional)
                f.write("-- Create table if not exists\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {table} (\n")
                f.write("    id SERIAL PRIMARY KEY,\n")
                f.write("    ticker VARCHAR(10) NOT NULL,\n")
                f.write("    time INTEGER NOT NULL,\n")
                f.write("    high FLOAT NOT NULL,\n")
                f.write("    low FLOAT NOT NULL,\n")
                f.write("    avg FLOAT NOT NULL,\n")
                f.write("    sale FLOAT NOT NULL,\n")
                f.write("    meta JSONB\n")
                f.write(");\n\n")
                
                # Write indexes
                f.write("-- Create indexes\n")
                f.write(f"CREATE INDEX IF NOT EXISTS idx_{table}_ticker ON {table}(ticker);\n")
                f.write(f"CREATE INDEX IF NOT EXISTS idx_{table}_time ON {table}(time);\n")
                f.write("\n")
                
                # Begin transaction
                f.write("-- Begin transaction\n")
                f.write("BEGIN;\n\n")
                
                # Fetch and write data in batches
                result = conn.execute(text(query))
                batch = []
                records_written = 0
                
                for row in result:
                    # Convert row to dict
                    record = {
                        'ticker': row.ticker,
                        'time': row.time,
                        'high': row.high,
                        'low': row.low,
                        'avg': row.avg,
                        'sale': row.sale,
                        'meta': row.meta
                    }
                    batch.append(record)
                    
                    # Write batch when full
                    if len(batch) >= batch_size:
                        write_batch(f, table, batch)
                        records_written += len(batch)
                        logger.debug(f"Written {records_written:,} records...")
                        batch = []
                
                # Write remaining records
                if batch:
                    write_batch(f, table, batch)
                    records_written += len(batch)
                
                # Commit transaction
                f.write("\n-- Commit transaction\n")
                f.write("COMMIT;\n\n")
                
                # Write summary
                f.write(f"-- Export completed: {records_written:,} records\n")
                
                logger.success(f"Export completed: {records_written:,} records written to {output}")
                
    except Exception as e:
        logger.error(f"Export failed: {type(e).__name__}: {e}")
        raise


def write_batch(file, table, batch):
    """Write a batch of records as an INSERT statement."""
    if not batch:
        return
    
    # Start INSERT statement
    file.write(f"INSERT INTO {table} (ticker, time, high, low, avg, sale, meta) VALUES\n")
    
    # Write values
    for i, record in enumerate(batch):
        # Escape single quotes in ticker
        ticker = record['ticker'].replace("'", "''")
        
        # Convert meta dict to JSON string
        meta_json = json.dumps(record['meta']) if record['meta'] else 'NULL'
        if meta_json != 'NULL':
            # Escape single quotes in JSON
            meta_json = "'" + meta_json.replace("'", "''") + "'::jsonb"
        
        # Write value tuple
        file.write(f"    ('{ticker}', {record['time']}, {record['high']}, "
                  f"{record['low']}, {record['avg']}, {record['sale']}, {meta_json})")
        
        # Add comma except for last record
        if i < len(batch) - 1:
            file.write(",\n")
        else:
            file.write(";\n")
    
    file.write("\n")


if __name__ == "__main__":
    main()