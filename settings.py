import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///stocks.db")

# API settings
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Default settings
DEFAULT_DAYS = 90
DEFAULT_INTERVAL = "minute"
DEFAULT_MULTIPLIER = 1

# Logging settings
LOG_FORMAT_DEBUG = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
LOG_FORMAT_INFO = "{time:HH:mm:ss} | {level} | {message}"

# Batch settings
BATCH_COMMIT_SIZE = 1000