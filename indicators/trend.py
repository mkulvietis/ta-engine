from typing import Any, Dict
import pandas as pd
import pandas_ta as ta
from .base import Indicator

class SMA(Indicator):
    @property
    def name(self) -> str:
        return "sma"

    @property
    def category(self) -> str:
        return "trend"

    @property
    def description(self) -> str:
        return "Simple Moving Average."

    @property
    def default_params(self) -> Dict[str, Any]:
        return {"length": 20}

    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        p = self.validate_params(params)
        length = p.get("length", p.get("period", 20))
        col = p.get("source", "close")
        
        if col not in df.columns:
            return {"error": f"Column {col} not found"}
        
        sma_series = df.ta.sma(close=col, length=length)
        if sma_series is None or sma_series.empty:
            return {"value": None}
            
        val = sma_series.iloc[-1]
        return {"value": float(val) if pd.notnull(val) else None}

class EMA(Indicator):
    @property
    def name(self) -> str:
        return "ema"

    @property
    def category(self) -> str:
        return "trend"

    @property
    def description(self) -> str:
        return "Exponential Moving Average."

    @property
    def default_params(self) -> Dict[str, Any]:
        return {"length": 20}

    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        p = self.validate_params(params)
        length = p.get("length", p.get("period", 20))
        col = p.get("source", "close")
        
        if col not in df.columns:
            return {"error": f"Column {col} not found"}

        ema_series = df.ta.ema(close=col, length=length)
        if ema_series is None or ema_series.empty:
            return {"value": None}
            
        val = ema_series.iloc[-1]
        return {"value": float(val) if pd.notnull(val) else None}
