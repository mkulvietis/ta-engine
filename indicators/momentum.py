from typing import Dict, Any
import pandas as pd
import pandas_ta as ta
from .base import Indicator

class RSI(Indicator):
    @property
    def name(self) -> str:
        return "rsi"

    @property
    def category(self) -> str:
        return "momentum"

    @property
    def description(self) -> str:
        return "Relative Strength Index. Measures the speed and change of price movements."

    @property
    def default_params(self) -> Dict[str, Any]:
        return {"length": 14}

    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        p = self.validate_params(params)
        length = p.get("length", p.get("period", 14)) # Handle both names for flexibility
        
        if len(df) < length:
            return {"value": None}

        # pandas-ta adds the result as a series
        rsi_series = df.ta.rsi(length=length)
        
        if rsi_series is None or rsi_series.empty:
            return {"value": None}
            
        val = rsi_series.iloc[-1]
        
        return {
            "value": float(val) if pd.notnull(val) else None
        }
