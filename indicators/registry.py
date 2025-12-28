from typing import Dict, List, Type, Any
from indicators.base import Indicator
# Import your indicators here to register them
from indicators.momentum import RSI
from indicators.trend import SMA, EMA
from indicators.volatility import ATR
from indicators.volume import VolumeSMA, CVD

class IndicatorRegistry:
    def __init__(self):
        self._indicators: Dict[str, Type[Indicator]] = {}
        self._instances: Dict[str, Indicator] = {}
        
        # Register known indicators
        self.register(RSI)
        self.register(SMA)
        self.register(EMA)
        self.register(ATR)
        self.register(VolumeSMA)
        self.register(CVD)

    def register(self, indicator_cls: Type[Indicator]):
        """Register a new indicator class."""
        instance = indicator_cls()
        self._indicators[instance.name] = indicator_cls
        self._instances[instance.name] = instance

    def get_indicator(self, name: str) -> Indicator:
        """Get an indicator instance by name."""
        if name not in self._instances:
            raise ValueError(f"Indicator '{name}' not found. Available: {list(self._instances.keys())}")
        return self._instances[name]

    def list_indicators(self) -> List[Dict[str, Any]]:
        """List all available indicators with metadata."""
        return [
            {
                "name": ind.name,
                "category": ind.category,
                "description": ind.description,
                "default_params": ind.default_params,
                "required_columns": ind.required_columns,
                "output_schema": ind.output_schema
            }
            for ind in self._instances.values()
        ]

# Global registry instance
registry = IndicatorRegistry()
