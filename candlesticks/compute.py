from typing import Any, Dict, List, Optional
import pandas as pd
from candlesticks.registry import pattern_registry

def detect_patterns(
    df: pd.DataFrame,
    cache: Optional[Any] = None,
    bar_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Detect all registered candlestick patterns in the given DataFrame.
    
    Args:
        df: DataFrame with price data (open, high, low, close)
        cache: Optional ResultCache instance for caching results
        bar_metadata: Optional metadata about the target bar:
                     {'ticker': str, 'day': int, 'minute': int, 'timeframe': int, 'is_final': bool}
        
    Returns:
        List of detected patterns with their metadata.
        Each pattern dict contains: name, classification, confidence, bar_index
    """
    # Check cache first
    use_cache = cache is not None and bar_metadata is not None
    if use_cache:
        ticker = bar_metadata['ticker']
        day = bar_metadata['day']
        minute = bar_metadata['minute']
        timeframe = bar_metadata['timeframe']
        is_final = bar_metadata.get('is_final', False)
        
        cached_patterns = cache.get_patterns(ticker, day, minute, timeframe)
        if cached_patterns is not None:
            return cached_patterns
    
    # Cache miss or no cache - detect patterns
    detected = []
    
    for pattern in pattern_registry.get_all_patterns():
        if len(df) >= pattern.required_bars:
            result = pattern.detect(df)
            if result:
                detected.append(result)
                
    # Sort by confidence descending
    detected.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Store in cache if bar is final
    if use_cache and is_final:
        cache.set_patterns(ticker, day, minute, timeframe, detected)
    
    return detected
