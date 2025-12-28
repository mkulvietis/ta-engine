from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ta-engine"}

@patch("server.indicators_tool.registry.list_indicators")
def test_list_indicators(mock_list):
    mock_list.return_value = [{"name": "rsi", "category": "momentum"}]
    response = client.get("/indicators")
    assert response.status_code == 200
    assert response.json() == [{"name": "rsi", "category": "momentum"}]

@patch("server.candlestick_tool.pattern_registry.list_patterns")
def test_list_patterns(mock_list):
    mock_list.return_value = [{"name": "Hammer", "classification": "Bullish"}]
    response = client.get("/candlesticks")
    assert response.status_code == 200
    assert response.json() == [{"name": "Hammer", "classification": "Bullish"}]

@patch("server.indicators_tool.client.fetch_bars")
@patch("server.indicators_tool.compute_indicators")
def test_compute_indicators(mock_compute, mock_fetch):
    # Mock data
    mock_fetch.return_value = pd.DataFrame([
        {"timestamp": "2023-01-01", "close": 100, "is_final": True}
    ])
    mock_compute.return_value = {"rsi": 50}

    payload = {
        "ticker": "AAPL",
        "indicators": {"rsi": {"length": 14}},
        "limit": 100
    }
    
    response = client.post("/indicators/calculations", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["results"] == {"rsi": 50}

@patch("server.candlestick_tool.client.fetch_bars")
@patch("server.candlestick_tool.detect_patterns")
def test_detect_candlesticks(mock_detect, mock_fetch):
    # Mock data
    mock_fetch.return_value = pd.DataFrame([
        {"timestamp": "2023-01-01", "close": 100, "is_final": True}
    ])
    mock_detect.return_value = [{"name": "Hammer", "confidence": 0.8}]

    payload = {
        "ticker": "AAPL",
        "limit": 100
    }
    
    response = client.post("/candlesticks/detections", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["patterns"] == [{"name": "Hammer", "confidence": 0.8}]
