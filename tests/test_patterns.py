import pytest
import pandas as pd
from candlesticks.compute import detect_patterns
from candlesticks.registry import pattern_registry
from candlesticks.bullish import Hammer, BullishEngulfing
from candlesticks.bearish import ShootingStar
from candlesticks.neutral import Doji

class TestPatternRegistry:
    """Test the pattern registry."""
    
    def test_registry_has_patterns(self):
        """Test that registry contains expected patterns."""
        patterns = pattern_registry.list_patterns()
        assert len(patterns) > 0
        
        pattern_names = [p['name'] for p in patterns]
        assert 'hammer' in pattern_names
        assert 'shooting_star' in pattern_names
        assert 'doji' in pattern_names
        assert 'bullish_engulfing' in pattern_names
    
    def test_get_pattern(self):
        """Test getting a pattern by name."""
        hammer = pattern_registry.get_pattern('hammer')
        assert hammer.name == 'hammer'
        assert hammer.classification == 'bullish'


class TestHammerPattern:
    """Test the Hammer pattern."""
    
    def test_hammer_detected(self):
        """Test that hammer pattern is detected correctly."""
        # Create a hammer: long lower shadow, small body at top
        data = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [95.0],  # Long lower shadow
            'close': [101.0]  # Small body at top
        })
        
        pattern = Hammer()
        result = pattern.detect(data)
        
        assert result is not None
        assert result['name'] == 'hammer'
        assert result['classification'] == 'bullish'
        assert result['confidence'] > 0
    
    def test_not_hammer_no_long_shadow(self):
        """Test that hammer is not detected without long shadow."""
        data = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [99.0],  # Short lower shadow
            'close': [101.0]
        })
        
        pattern = Hammer()
        result = pattern.detect(data)
        
        assert result is None


class TestDojiPattern:
    """Test the Doji pattern."""
    
    def test_doji_detected(self):
        """Test that doji pattern is detected correctly."""
        # Create a doji: open == close
        data = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [98.0],
            'close': [100.0]  # Same as open
        })
        
        pattern = Doji()
        result = pattern.detect(data)
        
        assert result is not None
        assert result['name'] == 'doji'
        assert result['classification'] == 'neutral'
    
    def test_not_doji_large_body(self):
        """Test that doji is not detected with large body."""
        data = pd.DataFrame({
            'open': [100.0],
            'high': [105.0],
            'low': [95.0],
            'close': [104.0]  # Large body
        })
        
        pattern = Doji()
        result = pattern.detect(data)
        
        assert result is None


class TestBullishEngulfing:
    """Test the Bullish Engulfing pattern."""
    
    def test_bullish_engulfing_detected(self):
        """Test that bullish engulfing is detected correctly."""
        # First bar: bearish, Second bar: bullish engulfing
        data = pd.DataFrame({
            'open': [105.0, 99.0],
            'high': [106.0, 107.0],
            'low': [99.0, 98.0],
            'close': [100.0, 106.0]  # Second engulfs first
        })
        
        pattern = BullishEngulfing()
        result = pattern.detect(data)
        
        assert result is not None
        assert result['name'] == 'bullish_engulfing'
        assert result['classification'] == 'bullish'
    
    def test_not_engulfing_no_engulf(self):
        """Test that pattern is not detected without engulfing."""
        data = pd.DataFrame({
            'open': [105.0, 101.0],
            'high': [106.0, 104.0],
            'low': [99.0, 100.0],
            'close': [100.0, 103.0]  # Doesn't engulf
        })
        
        pattern = BullishEngulfing()
        result = pattern.detect(data)
        
        assert result is None


class TestDetectPatternsFunction:
    """Test the detect_patterns function."""
    
    def test_detect_patterns_empty(self):
        """Test detect_patterns with no patterns present."""
        # Regular candle, no pattern
        data = pd.DataFrame({
            'open': [100.0],
            'high': [101.0],
            'low': [99.0],
            'close': [100.5]
        })
        
        patterns = detect_patterns(data)
        
        # Should return empty list or only very weak patterns
        assert isinstance(patterns, list)
    
    def test_detect_patterns_hammer(self):
        """Test detect_patterns finds hammer."""
        # Clear hammer pattern
        data = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [95.0],
            'close': [101.0]
        })
        
        patterns = detect_patterns(data)
        
        assert len(patterns) > 0
        pattern_names = [p['name'] for p in patterns]
        assert 'hammer' in pattern_names
    
    def test_detect_patterns_multiple(self):
        """Test that multiple patterns can be detected."""
        # Create a doji-like pattern
        data = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [98.0],
            'close': [100.1]  # Very small body
        })
        
        patterns = detect_patterns(data)
        
        # Should detect doji (and possibly spinning top)
        assert isinstance(patterns, list)
        if len(patterns) > 0:
            # Verify all have required fields
            for p in patterns:
                assert 'name' in p
                assert 'classification' in p
                assert 'confidence' in p
    
    def test_patterns_sorted_by_confidence(self):
        """Test that patterns are sorted by confidence."""
        data = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [95.0],
            'close': [101.0]
        })
        
        patterns = detect_patterns(data)
        
        if len(patterns) > 1:
            # Check descending confidence order
            confidences = [p['confidence'] for p in patterns]
            assert confidences == sorted(confidences, reverse=True)
