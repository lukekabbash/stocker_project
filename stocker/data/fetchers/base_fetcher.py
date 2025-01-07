from abc import ABC, abstractmethod
import pandas as pd

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass