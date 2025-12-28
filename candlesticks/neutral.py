from typing import Any, Dict, Optional
import pandas as pd
from candlesticks.base import Pattern

class Doji(Pattern):
    """
    Neutral indecision pattern where open and close are nearly equal.
    Indicates potential reversal or continuation depending on context.
    """
    
    @property
    def name(self) -> str:
        return "doji"
    
    @property
    def classification(self) -> str:
        return "neutral"
    
    @property
    def description(self) -> str:
        return "Indecision pattern where open equals close (or very close)"
    
    @property
    def required_bars(self) -> int:
        return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        total_range = last['high'] - last['low']
        
        if total_range == 0:
            return None
        
        # Doji criteria: body is very small compared to total range
        # Typically body should be < 5-10% of total range
        body_ratio = body / total_range
        
        if body_ratio < 0.1:  # Body is less than 10% of range
            # Confidence inversely related to body size
            confidence = 1.0 - (body_ratio / 0.1)
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(confidence, 2),
                'bar_index': len(df) - 1
            }
        
        return None


class SpinningTop(Pattern):
    """
    Neutral indecision pattern with small body and long shadows on both sides.
    Indicates uncertainty in the market.
    """
    
    @property
    def name(self) -> str:
        return "spinning_top"
    
    @property
    def classification(self) -> str:
        return "neutral"
    
    @property
    def description(self) -> str:
        return "Indecision pattern with small body and long upper and lower shadows"
    
    @property
    def required_bars(self) -> int:
        return 1
    
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        self.validate_dataframe(df)
        
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        upper_shadow = last['high'] - max(last['open'], last['close'])
        total_range = last['high'] - last['low']
        
        if total_range == 0 or body == 0:
            return None
        
        # Spinning top criteria:
        # 1. Small body (< 30% of range)
        # 2. Both shadows are longer than body
        # 3. Shadows are relatively balanced (not too different)
        body_ratio = body / total_range
        shadow_ratio = abs(upper_shadow - lower_shadow) / max(upper_shadow, lower_shadow, 0.001)
        
        if (body_ratio < 0.3 and
            lower_shadow > body and
            upper_shadow > body and
            shadow_ratio < 0.5):  # Shadows not too imbalanced
            
            # Confidence based on how balanced the pattern is
            balance_score = 1.0 - shadow_ratio
            size_score = 1.0 - (body_ratio / 0.3)
            confidence = (balance_score + size_score) / 2
            
            return {
                'name': self.name,
                'classification': self.classification,
                'confidence': round(confidence, 2),
                'bar_index': len(df) - 1
            }
        
        return None
