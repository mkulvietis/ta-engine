from typing import Any, Dict, List
import pandas as pd
from candlesticks.registry import pattern_registry

def detect_patterns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detect all registered candlestick patterns in the given DataFrame.
    
    Args:
        df: DataFrame with price data (open, high, low, close)
        
    Returns:
        List of detected patterns with their metadata.
        Each pattern dict contains: name, classification, confidence, bar_index
    """
    detected = []
    
    for pattern in pattern_registry.get_all_patterns():
        if len(df) >= pattern.required_bars:
            result = pattern.detect(df)
            if result:
                detected.append(result)
                
    # Sort by confidence descending
    detected.sort(key=lambda x: x['confidence'], reverse=True)
    
    return detected
