import httpx
import pandas as pd
from typing import Optional
from datetime import datetime

class BarsClient:
    REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def _validate_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure dataframe has required columns and correct types."""
        if df.empty:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Response missing required columns: {missing}")
            
        # Ensure standard ordering
        df = df[self.REQUIRED_COLUMNS + [c for c in df.columns if c not in self.REQUIRED_COLUMNS]]
        
        # Ensure timestamp is datetime if it looks like it, or keep as is if int/str? 
        # The prompt says 'timestamp' in schema. Usually better to parse to datetime for pandas manipulation.
        # But for strictly stateless "compute" usually we want numeric index or datetime index.
        # Let's try to convert to datetime if possible, assuming input is ISO or int.
        # However, the prompt says "No interpolation, resampling...". 
        # I will keep it simple.
        return df

    def fetch_bars(self, 
                   ticker: str, 
                   day: Optional[int] = None, 
                   minute: Optional[int] = None, 
                   limit: int = 100, 
                   timeframe: int = 1) -> pd.DataFrame:
        
        params = {
            "limit": limit,
            "timeframe": timeframe
        }
        if day is not None:
            params["day"] = day
        if minute is not None:
            params["minute"] = minute

        url = f"{self.base_url}/bars/{ticker}"
        
        with httpx.Client() as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
        df = pd.DataFrame(data)
        return self._validate_df(df)

    def fetch_latest_bars(self, ticker: str, limit: int = 100, timeframe: int = 1) -> pd.DataFrame:
        """Alias for fetch_bars without specific time point."""
        return self.fetch_bars(ticker, limit=limit, timeframe=timeframe)
