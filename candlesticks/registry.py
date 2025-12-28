from typing import Dict, List, Type, Any
from candlesticks.base import Pattern

# Import pattern classes to register them
from candlesticks.bullish import (
    Hammer, MorningStar, BullishEngulfing, 
    ThreeWhiteSoldiers, BullishHarami, PiercingLine, 
    InvertedHammer, BullishMarubozu, TweezerBottom
)
from candlesticks.bearish import (
    ShootingStar, EveningStar, BearishEngulfing,
    ThreeBlackCrows, BearishHarami, DarkCloudCover,
    HangingMan, BearishMarubozu, TweezerTop
)
from candlesticks.neutral import Doji, SpinningTop

class PatternRegistry:
    def __init__(self):
        self._patterns: Dict[str, Type[Pattern]] = {}
        self._instances: Dict[str, Pattern] = {}
        
        # Register all known patterns
        # Bullish
        self.register(Hammer)
        self.register(MorningStar)
        self.register(BullishEngulfing)
        self.register(ThreeWhiteSoldiers)
        self.register(BullishHarami)
        self.register(PiercingLine)
        self.register(InvertedHammer)
        self.register(BullishMarubozu)
        self.register(TweezerBottom)
        
        # Bearish
        self.register(ShootingStar)
        self.register(EveningStar)
        self.register(BearishEngulfing)
        self.register(ThreeBlackCrows)
        self.register(BearishHarami)
        self.register(DarkCloudCover)
        self.register(HangingMan)
        self.register(BearishMarubozu)
        self.register(TweezerTop)
        
        # Neutral
        self.register(Doji)
        self.register(SpinningTop)

    def register(self, pattern_cls: Type[Pattern]):
        """Register a new pattern class."""
        instance = pattern_cls()
        self._patterns[instance.name] = pattern_cls
        self._instances[instance.name] = instance

    def get_pattern(self, name: str) -> Pattern:
        """Get a pattern instance by name."""
        if name not in self._instances:
            raise ValueError(f"Pattern '{name}' not found. Available: {list(self._instances.keys())}")
        return self._instances[name]

    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all available patterns with metadata."""
        return [
            {
                "name": pat.name,
                "classification": pat.classification,
                "description": pat.description,
                "required_bars": pat.required_bars
            }
            for pat in self._instances.values()
        ]
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all registered pattern instances."""
        return list(self._instances.values())

# Global registry instance
pattern_registry = PatternRegistry()
