from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel

class Indicator(ABC):
    """
    Abstract base class for all technical indicators.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the indicator (e.g., 'rsi', 'sma')."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category of the indicator (e.g., 'momentum', 'trend')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the indicator does."""
        pass

    @property
    def default_params(self) -> Dict[str, Any]:
        """Default parameters for the indicator."""
        return {}

    @property
    def required_columns(self) -> List[str]:
        """List of columns required in the input DataFrame."""
        return ["close"]

    @property
    def output_schema(self) -> Dict[str, str]:
        """Description of the output dictionary keys and types."""
        return {"value": "float"}

    @abstractmethod
    def compute(self, df: pd.DataFrame, **params) -> Dict[str, Any]:
        """
        Compute the indicator.
        
        Args:
            df: Input DataFrame containing market data.
            **params: Indicator-specific parameters.
            
        Returns:
            Dictionary containing the computed results. 
            Should be JSON-serializable (no numpy types).
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge provided params with defaults."""
        final_params = self.default_params.copy()
        if params:
            final_params.update(params)
        return final_params
