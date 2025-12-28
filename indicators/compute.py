from typing import Any, Dict, List, Optional
import pandas as pd
from indicators.registry import registry

def compute_indicators(
    df: pd.DataFrame,
    indicators: Dict[str, Dict[str, Any]],
    cache: Optional[Any] = None,
    bar_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Pure, stateless computation of requested indicators.
    
    Args:
        df: The market data DataFrame.
        indicators: Dictionary mapping indicator names to their parameters.
                    e.g. {'rsi': {'length': 14}, 'sma': {'length': 50}}
        cache: Optional ResultCache instance for caching results
        bar_metadata: Optional metadata about the target bar:
                     {'ticker': str, 'day': int, 'minute': int, 'timeframe': int, 'is_final': bool}
                
    Returns:
        Dictionary mapping indicator names to their computed results.
    """
    results = {}
    
    # Extract metadata for caching
    use_cache = cache is not None and bar_metadata is not None
    if use_cache:
        ticker = bar_metadata['ticker']
        day = bar_metadata['day']
        minute = bar_metadata['minute']
        timeframe = bar_metadata['timeframe']
        is_final = bar_metadata.get('is_final', False)
    
    for name, ind_params in indicators.items():
        try:
            # Check cache first
            if use_cache:
                cached_result = cache.get_indicator(
                    ticker, day, minute, timeframe, name, ind_params or {}
                )
                if cached_result is not None:
                    results[name] = cached_result
                    continue
            
            # Cache miss or no cache - compute
            indicator = registry.get_indicator(name)
            res = indicator.compute(df, **(ind_params or {}))
            results[name] = res
            
            # Store in cache if bar is final
            if use_cache and is_final:
                cache.set_indicator(
                    ticker, day, minute, timeframe, name, ind_params or {}, res
                )
                
        except Exception as e:
            results[name] = {"error": str(e)}
            
    return results
