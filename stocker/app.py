import subprocess
import sys
import os
import asyncio
from dash import Dash, Input, Output, State
import dash_bootstrap_components as dbc
from flask_caching import Cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from ui.layout import create_layout
from data.fetchers.yahoo_fetcher import YahooFetcher
from data.fetchers.processors.data_processor import process_stock_data
from visualization.plotter import plot_multi_stock_chart
from config import CACHE_DIR, CACHE_TIMEOUT, DATABASE_URL

# Automatically verify and install required packages
def install_and_verify_packages():
    """Ensure required packages are installed."""
    required_packages = {
        "dash": "2.9.3",
        "dash-bootstrap-components": "1.3.1",
        "flask-caching": "1.10.1",
        "SQLAlchemy": "1.4.46",
        "pandas": "1.5.3",
        "numpy": "1.24.3",
        "yfinance": "0.2.24",
        "plotly": "5.15.0",
        "python-dotenv": "1.0.0",
        "aiohttp": "3.8.4",
    }

    for package, version in required_packages.items():
        try:
            import importlib.metadata
            installed_version = importlib.metadata.version(package)
            if installed_version != version:
                raise ImportError(f"Version mismatch for {package}. Installed: {installed_version}, Required: {version}")
        except ImportError:
            print(f"Installing or upgrading package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}=={version}"])

install_and_verify_packages()

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Stocker 4.2.2"
app.layout = create_layout()

# Initialize Cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': CACHE_DIR,
    'CACHE_THRESHOLD': 5000  # Adjust as needed
})

# Database Setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create tables if they don't exist
from data.models.stock_data import Base
Base.metadata.create_all(engine)

# Sample list of 1000 stock tickers
# Replace this list with actual stock tickers
TOP_1000_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "BRK.B", "NVDA", "JPM", "V",
    # Add more tickers here
]

# Cache the top 1000 stocks data on startup
@app.server.before_first_request
async def startup_cache():
    fetcher = YahooFetcher()
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    start_date = (pd.Timestamp.today() - pd.Timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Fetch data
    print("Fetching data for top 1000 stocks...")
    top_1000_data = await fetcher.fetch_top_1000_stocks(start_date, end_date, TOP_1000_STOCKS)
    
    # Process and cache data
    for ticker, data in top_1000_data.items():
        processed_data = process_stock_data(data)
        cache.set(f"stock_data_{ticker}", processed_data.to_json(date_format='iso', orient='split'))
    print("Caching complete.")

@app.callback(
    Output("multi-stock-graph", "figure"),
    Output("error-message", "children"),
    Input("fetch-data-button", "n_clicks"),
    State("ticker-input", "value"),
    State("date-picker-range", "start_date"),
    State("date-picker-range", "end_date"),
    State("indicators-checklist", "value")
)
def update_multi_stock_graph(n_clicks, tickers, start_date, end_date, indicators):
    if n_clicks == 0:
        return {}, ""
    
    if not tickers:
        return {}, "Please enter valid ticker symbols."
    
    tickers_list = [ticker.strip().upper() for ticker in tickers.split(',')]
    dfs = {}
    fetcher = YahooFetcher()
    error_messages = []
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def fetch_and_process(ticker):
        cached_data = cache.get(f"stock_data_{ticker}")
        if cached_data:
            df = pd.read_json(cached_data, orient='split', convert_dates=['index'])
            df.index = pd.to_datetime(df.index)
            # Filter the data for the date range
            df = df.loc[start_date:end_date]
        else:
            df = await fetcher.fetch_data(ticker, start_date, end_date)
            if not df.empty:
                df = process_stock_data(df)
                cache.set(f"stock_data_{ticker}", df.to_json(date_format='iso', orient='split'))
        return ticker, df
    
    tasks = [fetch_and_process(ticker) for ticker in tickers_list]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    
    for ticker, df in results:
        if df.empty:
            error_messages.append(f"No data found for ticker '{ticker}'.")
            continue
        dfs[ticker] = df
    
    if not dfs:
        error_message = " | ".join(error_messages) if error_messages else "No data could be fetched for the provided tickers."
        return {}, error_message
    
    fig = plot_multi_stock_chart(dfs, indicators)
    error_message = " | ".join(error_messages) if error_messages else ""
    
   