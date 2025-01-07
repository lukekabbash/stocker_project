import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
YAHOO_API_KEY = os.getenv("YAHOO_API_KEY", None)
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", None)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", None)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", None)

# Cache Settings
CACHE_DIR = 'cache-directory'
CACHE_TIMEOUT = 60 * 60  # 1 hour in seconds

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///stocker.db")