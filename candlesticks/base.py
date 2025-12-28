from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd

class Pattern(ABC):
    """
    Abstract base class for all candlestick patterns.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the pattern (e.g., 'hammer', 'doji')."""
        pass

    @property
    @abstractmethod
    def classification(self) -> str:
        """Classification: 'bullish', 'bearish', or 'neutral'."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the pattern."""
        pass

    @property
    def required_bars(self) -> int:
        """Number of bars needed to detect this pattern (3-5)."""
        return 3

    @abstractmethod
    def detect(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Detect pattern in the most recent bars.
        
        Args:
            df: Input DataFrame containing market data.
                Must have at least 'open', 'high', 'low', 'close' columns.
                
        Returns:
            Detection result dictionary if pattern is found, None otherwise.
            Format: {
                'name': str,
                'classification': str,
                'confidence': float (0.0-1.0),
                'bar_index': int (index of the pattern completion bar)
            }
        """
        pass
    
    def validate_dataframe(self, df: pd.DataFrame) -> None:
        """Validate that DataFrame has required columns and enough bars."""
        required_cols = ['open', 'high', 'low', 'close']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"DataFrame missing required columns: {missing}")
        
        if len(df) < self.required_bars:
            raise ValueError(
                f"Pattern '{self.name}' requires at least {self.required_bars} bars, "
                f"but only {len(df)} provided"
            )
