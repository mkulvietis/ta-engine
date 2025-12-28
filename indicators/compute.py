from typing import Any, Dict, List, Optional
import pandas as pd
from indicators.registry import registry

def compute_indicators(
    df: pd.DataFrame,
    indicators: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Pure, stateless computation of requested indicators.
    
    Args:
        df: The market data DataFrame.
        indicators: Dictionary mapping indicator names to their parameters.
                    e.g. {'rsi': {'length': 14}, 'sma': {'length': 50}}
                
    Returns:
        Dictionary mapping indicator names to their computed results.
    """
    results = {}
    
    for name, ind_params in indicators.items():
        try:
            indicator = registry.get_indicator(name)
            
            # Compute
            # Use empty dict if params is None/missing
            res = indicator.compute(df, **(ind_params or {}))
            results[name] = res
        except Exception as e:
            results[name] = {"error": str(e)}
            
    return results
