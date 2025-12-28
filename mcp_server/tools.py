from typing import List, Dict, Any, Optional
from data.bars_client import BarsClient
from indicators.compute import compute_indicators
from indicators.registry import registry

client = BarsClient()

def list_indicators() -> List[Dict[str, Any]]:
    """
    List all available technical indicators and their metadata.
    """
    return registry.list_indicators()

def compute_indicators_tool(
    ticker: str,
    indicators: Dict[str, Dict[str, Any]],
    limit: int = 100,
    timeframe: int = 1,
    day: Optional[int] = None,
    minute: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetch market data for a ticker and compute technical indicators.

    Args:
        ticker: The asset symbol (e.g., 'AAPL', 'BTCUSD').
        indicators: Dictionary mapping indicator names to their parameters.
                    Example: {'rsi': {'period': 14}, 'sma': {'period': 50}}
        limit: Number of bars to fetch (default: 100).
        timeframe: Bar aggregation timeframe in minutes (default: 1).
        day: Specific day to fetch (YYYYMMDD).
        minute: Specific minute to fetch backwards from (HHMM).

    Returns:
        Dictionary containing the computed results for each requested indicator.
    """
    # 1. Fetch Request
    df = client.fetch_bars(ticker, day=day, minute=minute, limit=limit, timeframe=timeframe)

    if df.empty:
        return {"error": "No data found", "ticker": ticker}

    # 2. Compute
    results = compute_indicators(df, indicators)
    
    # 3. Return
    return {
        "ticker": ticker,
        "last_timestamp": str(df["timestamp"].iloc[-1]) if not df.empty else None,
        "results": results
    }

def fetch_bars_tool(
    ticker: str,
    limit: int = 100,
    timeframe: int = 1,
    day: Optional[int] = None,
    minute: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetch raw market data bars for a ticker.

    Args:
        ticker: The asset symbol (e.g., 'AAPL', 'BTCUSD').
        limit: Number of bars to fetch (default: 100).
        timeframe: Bar aggregation timeframe in minutes (default: 1).
        day: Specific day to fetch (YYYYMMDD).
        minute: Specific minute to fetch backwards from (HHMM).

    Returns:
        List of bar dictionaries.
    """
    df = client.fetch_bars(ticker, day=day, minute=minute, limit=limit, timeframe=timeframe)
    return df.to_dict(orient="records")
