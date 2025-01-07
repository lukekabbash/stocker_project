import yfinance as yf
import pandas as pd
from .base_fetcher import BaseFetcher
import asyncio
from typing import List, Dict

class YahooFetcher(BaseFetcher):
    async def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            if data.empty:
                raise ValueError(f"No data found for ticker '{ticker}'.")
            return data
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance for {ticker}: {e}")
            return pd.DataFrame()
    
    async def fetch_top_1000_stocks(self, start_date: str, end_date: str, stock_list: List[str]) -> Dict[str, pd.DataFrame]:
        tasks = [self.fetch_data(stock, start_date, end_date) for stock in stock_list]
        results = await asyncio.gather(*tasks)
        return {stock: result for stock, result in zip(stock_list, results) if not result.empty}