from typing import Any, Dict
import pandas as pd
import pandas_ta as ta
from .base import Indicator

class ATR(Indicator):
    @property
    def name(self) -> str:
        return "atr"

    @property
    def category(self) -> str:
        return "volatility"

    @property
    def description(self) -> str:
        return "Average True Range."

    @property
    def default_params(self) -> Dict[str, Any]:
        return {"length": 14}
    
    @property
    def required_columns(self):
        return ["high", "low", "close"]

    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        p = self.validate_params(params)
        length = p.get("length", p.get("period", 14))
        
        atr_series = df.ta.atr(length=length)
        if atr_series is None or atr_series.empty:
            return {"value": None}
            
        val = atr_series.iloc[-1]
        return {"value": float(val) if pd.notnull(val) else None}
