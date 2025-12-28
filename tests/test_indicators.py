import pytest
import pandas as pd
import numpy as np
from indicators.momentum import RSI
from indicators.trend import SMA, EMA
from indicators.volatility import ATR
from indicators.volume import VolumeSMA, CVD
from indicators.compute import compute_indicators

@pytest.fixture
def sample_df():
    # Generate 100 bars of synthetic data
    dates = pd.date_range(start="2023-01-01", periods=100, freq="1min")
    df = pd.DataFrame({
        "timestamp": dates,
        "open": np.linspace(100, 110, 100),
        "high": np.linspace(101, 111, 100),
        "low": np.linspace(99, 109, 100),
        "close": np.linspace(100, 110, 100) + np.sin(np.linspace(0, 10, 100)), # Add some wave
        "volume": np.random.randint(100, 1000, 100).astype(float)
    })
    return df

def test_rsi(sample_df):
    rsi = RSI()
    res = rsi.compute(sample_df, period=14)
    assert "value" in res
    assert isinstance(res["value"], float)
    assert 0 <= res["value"] <= 100

def test_sma(sample_df):
    sma = SMA()
    res = sma.compute(sample_df, period=10)
    assert "value" in res
    assert isinstance(res["value"], float)

def test_ema(sample_df):
    ema = EMA()
    res = ema.compute(sample_df, period=10)
    assert "value" in res
    assert isinstance(res["value"], float)

def test_atr(sample_df):
    atr = ATR()
    res = atr.compute(sample_df, period=14)
    assert "value" in res
    assert isinstance(res["value"], float)

def test_volume_sma(sample_df):
    vsma = VolumeSMA()
    res = vsma.compute(sample_df, period=5)
    assert "value" in res
    assert isinstance(res["value"], float)

def test_cvd(sample_df):
    cvd = CVD()
    res = cvd.compute(sample_df)
    assert "value" in res
    assert isinstance(res["value"], float)

def test_compute_indicators_integration(sample_df):
    indicators = {
        "rsi": {"period": 14},
        "sma": {"period": 20},
        "ema": {"period": 10},
        "atr": {"period": 14},
        "volume_sma": {"period": 5},
        "cvd": {}
    }
    results = compute_indicators(sample_df, indicators)
    
    assert all(name in results for name in indicators)
    for name in indicators:
        assert "value" in results[name]
        assert results[name]["value"] is not None

def test_registry_list():
    from indicators.registry import registry
    indicators = registry.list_indicators()
    assert len(indicators) >= 5
    names = [i["name"] for i in indicators]
    assert "rsi" in names
    assert "sma" in names

def test_invalid_indicator(sample_df):
    results = compute_indicators(sample_df, {"non_existent": {}})
    assert "non_existent" in results
    assert "error" in results["non_existent"]

def test_empty_dataframe():
    empty_df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    results = compute_indicators(empty_df, {"rsi": {"period": 14}})
    assert results["rsi"]["value"] is None

def test_insufficient_data():
    tiny_df = pd.DataFrame({
        "close": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "volume": [10.0, 20.0]
    })
    # RSI 14 needs at least 15 bars for a value
    results = compute_indicators(tiny_df, {"rsi": {"period": 14}})
    assert results["rsi"]["value"] is None
