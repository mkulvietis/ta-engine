import pytest
import pandas as pd
import httpx
from data.bars_client import BarsClient

def test_client_fetch_latest_bars(respx_mock):
    client = BarsClient(base_url="http://testserver")
    
    # Mock the response
    mock_data = [
        {"timestamp": "2023-01-01T00:00:00", "open": 100, "high": 105, "low": 95, "close": 102, "volume": 1000}
    ]
    # Now calls /bars/AAPL without params (or with limit/timeframe)
    respx_mock.get("http://testserver/bars/AAPL").mock(return_value=httpx.Response(200, json=mock_data))
    
    df = client.fetch_latest_bars("AAPL", limit=1)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "close" in df.columns
    assert df.iloc[0]["close"] == 102

def test_client_fetch_bars_backwards(respx_mock):
    client = BarsClient(base_url="http://testserver")
    
    respx_mock.get("http://testserver/bars/AAPL").mock(return_value=httpx.Response(200, json=[]))
    
    df = client.fetch_bars("AAPL", day=20230101, minute=1000)
    
    assert isinstance(df, pd.DataFrame)
    # Check that query params were passed if possible (respx helps here)
    assert respx_mock.calls[0].request.url.params["day"] == "20230101"
    assert respx_mock.calls[0].request.url.params["minute"] == "1000"
