from typing import List, Dict, Any, Optional
from data.bars_client import BarsClient
from candlesticks.compute import detect_patterns
from candlesticks.registry import pattern_registry
from cache import global_cache

client = BarsClient()

def list_patterns_tool() -> List[Dict[str, Any]]:
    """
    List all available candlestick patterns and their metadata.
    """
    return pattern_registry.list_patterns()

def detect_patterns_tool(
    ticker: str,
    limit: int = 100,
    timeframe: int = 1,
    day: Optional[int] = None,
    minute: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetch market data for a ticker and detect candlestick patterns.

    Args:
        ticker: The asset symbol (e.g., 'AAPL', 'BTCUSD').
        limit: Number of bars to fetch (default: 100).
        timeframe: Bar aggregation timeframe in minutes (default: 1).
        day: Specific day to fetch (YYYYMMDD).
        minute: Specific minute to fetch backwards from (HHMM).

    Returns:
        Dictionary containing the detected patterns and metadata.
    """
    # 1. Fetch Request
    df = client.fetch_bars(ticker, day=day, minute=minute, limit=limit, timeframe=timeframe)

    if df.empty:
        return {"error": "No data found", "ticker": ticker, "patterns": []}

    # 2. Extract metadata from last bar for caching
    last_bar = df.iloc[-1]
    bar_metadata = {
        'ticker': ticker,
        'day': int(last_bar.get('trade_day', day or 0)),
        'minute': int(last_bar.get('minute_of_day', minute or 0)),
        'timeframe': timeframe,
        'is_final': bool(last_bar.get('is_final', False))
    }

    # 3. Compute with cache
    patterns = detect_patterns(df, cache=global_cache, bar_metadata=bar_metadata)
    
    # 4. Return
    return {
        "ticker": ticker,
        "last_timestamp": str(df["timestamp"].iloc[-1]) if not df.empty else None,
        "patterns": patterns
    }
