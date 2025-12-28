from typing import Any, Dict
import pandas as pd
import pandas_ta as ta
from .base import Indicator

class VolumeSMA(Indicator):
    @property
    def name(self) -> str:
        return "volume_sma"

    @property
    def category(self) -> str:
        return "volume"

    @property
    def description(self) -> str:
        return "Volume Simple Moving Average."

    @property
    def default_params(self) -> Dict[str, Any]:
        return {"length": 20}
    
    @property
    def required_columns(self):
        return ["volume"]

    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        p = self.validate_params(params)
        length = p.get("length", p.get("period", 20))
        
        # We can use SMA on volume
        sma_series = df.ta.sma(close="volume", length=length)
        if sma_series is None or sma_series.empty:
            return {"value": None}
            
        val = sma_series.iloc[-1]
        
        return {"value": float(val) if pd.notnull(val) else None}

class CVD(Indicator):
    @property
    def name(self) -> str:
        return "cvd"

    @property
    def category(self) -> str:
        return "volume"

    @property
    def description(self) -> str:
        return "Cumulative Volume Delta (Approximated from bar direction)."

    @property
    def default_params(self) -> Dict[str, Any]:
        return {} # No length usually for cumulative, but could have a window
    
    @property
    def required_columns(self):
        return ["open", "close", "volume"]

    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        if df.empty:
            return {"value": None}

        # Calculate Delta: Volume if Close >= Open, else -Volume
        # This is the most common OHLCV approximation of Delta.
        delta = df["volume"].copy()
        delta.loc[df["close"] < df["open"]] *= -1
        
        # Cumulative Sum
        cvd_series = delta.cumsum()
        
        val = cvd_series.iloc[-1]
        
        return {"value": float(val) if pd.notnull(val) else None}
