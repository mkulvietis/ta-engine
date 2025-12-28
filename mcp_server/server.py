from mcp.server.fastmcp import FastMCP
from .tools import list_indicators, compute_indicators_tool, fetch_bars_tool

# Initialize FastMCP server
mcp = FastMCP("Technical Analysis Engine")

@mcp.tool()
def registry_catalog() -> list[dict]:
    """Catalog of all available technical indicators and their schemata."""
    return list_indicators()

@mcp.tool()
def analyze(
    ticker: str,
    indicators: dict[str, dict],
    limit: int = 100,
    timeframe: int = 1,
    day: int = None,
    minute: int = None
) -> dict:
    """
    Analyze a market ticker with requested technical indicators.
    
    Args:
        ticker: Symbol to analyze (e.g. 'SPY').
        indicators: Dictionary of indicator names to their parameters.
                    Example: {'rsi': {'period': 14}, 'sma': {'period': 50}}
        limit: Max bars to fetch (default 100).
        timeframe: Minutes per bar (default 1).
        day: Specific date YYYYMMDD.
        minute: Specific minute HHMM (backwards from).
    """
    return compute_indicators_tool(
        ticker=ticker,
        indicators=indicators,
        limit=limit,
        timeframe=timeframe,
        day=day,
        minute=minute
    )

@mcp.tool()
def get_bars(
    ticker: str,
    limit: int = 100,
    timeframe: int = 1,
    day: int = None,
    minute: int = None
) -> list[dict]:
    """
    Fetch market data bars for a ticker.
    
    Args:
        ticker: Symbol to analyze (e.g. 'SPY').
        limit: Max bars to fetch (default 100).
        timeframe: Minutes per bar (default 1).
        day: Specific date YYYYMMDD.
        minute: Specific minute HHMM (backwards from).
    """
    return fetch_bars_tool(
        ticker=ticker,
        limit=limit,
        timeframe=timeframe,
        day=day,
        minute=minute
    )

if __name__ == "__main__":
    mcp.run()
