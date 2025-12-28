# Technical Analysis Engine

## Overview
This is a production-grade Python codebase for a Technical Analysis Engine. It is designed to be:
- **Pure & Stateless**: The computation layer is independent of data sources and IO.
- **MCP-Native**: Exposes functionality via the Model Context Protocol for LLM agents.
- **Extensible**: Easy to add new indicators via a plugin-like registry system.

## Architecture

### 1. Data Access Layer (`data/`)
Handles communication with the external market data service.
- Client validation
- DataFrame construction

### 2. Indicators (`indicators/`)
Modular indicator definitions. Each indicator is a self-contained class complying with the `Indicator` interface.

### 3. Registry (`registry.py`)
Central directory of available indicators, used for discovery and dynamic dispatch.

### 4. Computation (`compute.py`)
Pure functional core.
`DataFrame` + `Requests` -> `Results`

### 5. MCP Layer (`mcp/`)
Exposes the engine as an MCP server.
- `list_indicators`: Discover what can be computed.
- `compute_indicators`: End-to-end data fetch and computation.

## Setup

```bash
# Create venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install deps
pip install -r requirements.txt

# Run MCP Server
python -m mcp_server.server
```

## Usage

### Local Python
```python
from data.bars_client import BarsClient
from registry import registry
from compute import compute_indicators
from mcp_server.tools import compute_indicators_tool # or standard usage

client = BarsClient(base_url="http://localhost:8000")
df = client.fetch_latest_bars("AAPL", limit=100)
results = compute_indicators(df, ["rsi", "sma"], {"rsi": {"period": 14}, "sma": {"period": 20}})
print(results)
```
