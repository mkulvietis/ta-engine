from fastapi import APIRouter
from mcp.server.fastmcp import FastMCP
from .indicators_tool import list_indicators, compute_indicators_tool, fetch_bars_tool
from .candlestick_tool import list_patterns_tool, detect_patterns_tool

# Initialize FastMCP server
mcp = FastMCP("Technical Analysis Engine")

# Initialize FastAPI Router
router = APIRouter()

# --- Registry ---

@router.get("/indicators")
@mcp.tool()
def registry_catalog() -> list[dict]:
    """Catalog of all available technical indicators and their schemata."""
    return list_indicators()

@router.get("/candlesticks")
@mcp.tool()
def list_patterns() -> list[dict]:
    """Catalog of all available candlestick patterns."""
    return list_patterns_tool()

# --- Compute ---

@router.post("/indicators/calculations")
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
                    Example: {'rsi': {'length': 14}, 'sma': {'length': 50}}
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

@router.post("/candlesticks/detections")
@mcp.tool()
def detect_candlesticks(
    ticker: str,
    limit: int = 100,
    timeframe: int = 1,
    day: int = None,
    minute: int = None
) -> dict:
    """
    Detect candlestick patterns for a ticker.
    
    Args:
        ticker: Symbol to analyze (e.g. 'SPY').
        limit: Max bars to fetch (default 100).
        timeframe: Minutes per bar (default 1).
        day: Specific date YYYYMMDD.
        minute: Specific minute HHMM (backwards from).
    """
    return detect_patterns_tool(
        ticker=ticker,
        limit=limit,
        timeframe=timeframe,
        day=day,
        minute=minute
    )

# --- Data Access ---

@router.get("/bars/{ticker}")
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

# For standalone MCP execution
if __name__ == "__main__":
    mcp.run()
