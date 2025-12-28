from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add ta-engine directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.indicators_tool import fetch_bars_tool

@patch("server.indicators_tool.client")
def test_fetch_bars_tool(mock_client):
    """Test standard fetch_bars_tool usage"""
    # Setup
    df = pd.DataFrame([{"close": 100, "timestamp": "2023-01-01"}])
    mock_client.fetch_bars.return_value = df
    
    # Execute
    result = fetch_bars_tool("AAPL", limit=50)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["close"] == 100
    mock_client.fetch_bars.assert_called_with("AAPL", day=None, minute=None, limit=50, timeframe=1)

@patch("mcp_server.tools.client")
def test_fetch_bars_tool_empty(mock_client):
    """Test fetch_bars_tool with empty response"""
    # Setup
    df = pd.DataFrame([])
    mock_client.fetch_bars.return_value = df
    
    # Execute
    result = fetch_bars_tool("AAPL")
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 0
