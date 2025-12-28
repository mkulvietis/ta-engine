# Technical Analysis Engine

## Overview
A high-performance, stateless Technical Analysis Engine supporting dozens of indicators and 20+ candlestick patterns. 
- **Modularity**: Every indicator and pattern is a self-contained class.
- **Context-Aware**: Reversal patterns (e.g., Three White Soldiers) validate leading context to ensure high-quality detection.
- **MCP-Native**: Designed for seamless integration with AI agents via Model Context Protocol.

## Architecture

The engine is organized into domain-specific modules for maximum clarity and maintainability:

### 1. Indicators (`indicators/`)
Contains indicator implementations (Trend, Volatility, Momentum, Volume).
- `registry.py`: Centralized indicator discovery.
- `compute.py`: Pure function for batch indicator calculation.

### 2. Candlesticks (`candlesticks/`)
Advanced pattern recognition library.
- **Support**: 9 Bullish, 9 Bearish, and 2 Neutral patterns.
- `registry.py`: Centralized pattern discovery.
- `compute.py`: Detection engine that evaluates patterns across time series data.

### 3. Data Layer (`data/`)
Lightweight client for fetching market bars from the ingestion service.

### 4. MCP Layer (`mcp_server/`)
Exposes tools for discovery, indicator calculation, and pattern detection to LLM agents.

## Supported Patterns

| Bullish | Bearish | Neutral |
| :--- | :--- | :--- |
| Hammer | Shooting Star | Doji |
| Morning Star | Evening Star | Spinning Top |
| Bullish Engulfing | Bearish Engulfing | |
| Three White Soldiers* | Three Black Crows* | |
| Bullish Harami | Bearish Harami | |
| Piercing Line | Dark Cloud Cover | |
| Inverted Hammer | Hanging Man | |
| Bullish Marubozu | Bearish Marubozu | |
| Tweezer Bottom | Tweezer Top | |

*\*Context-validated: Requires 4 bars to ensure reversal vs continuation.*

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP Server
python -m mcp_server.server
```

## Usage

### Local Python Example
```python
from data.bars_client import BarsClient
from indicators.compute import compute_indicators
from candlesticks.compute import detect_patterns

client = BarsClient(base_url="http://localhost:8000")
df = client.fetch_latest_bars("BTCUSDT", limit=100)

# 1. Compute Indicators
indicators_to_run = {
    "rsi": {"length": 14},
    "sma": {"length": 50}
}
results = compute_indicators(df, indicators_to_run)

# 2. Detect Candlestick Patterns
detected = detect_patterns(df)
for p in detected:
    print(f"Found {p['name']} ({p['classification']}) with {p['confidence']*100}% confidence")
```

## Testing
The engine includes a comprehensive test suite covering all indicators and patterns.
```bash
pytest -v
```
