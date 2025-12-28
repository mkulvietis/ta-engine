import pytest
import pandas as pd
from cache import ResultCache, _make_params_key


class TestResultCache:
    """Test the ResultCache class."""
    
    def test_params_key_consistency(self):
        """Test that parameter key generation is consistent."""
        params1 = {"length": 14, "smoothing": 3}
        params2 = {"smoothing": 3, "length": 14}  # Different order
        
        # Should produce same key regardless of insertion order
        assert _make_params_key(params1) == _make_params_key(params2)
    
    def test_params_key_empty(self):
        """Test empty params produce empty frozenset."""
        assert _make_params_key({}) == frozenset()
    
    def test_indicator_cache_hit(self):
        """Test cache hit for indicators."""
        cache = ResultCache()
        
        # Store a result
        cache.set_indicator(
            ticker="BTCUSDT",
            day=20241228,
            minute=930,
            timeframe=1,
            indicator_name="rsi",
            params={"length": 14},
            value={"rsi": 65.5}
        )
        
        # Retrieve it
        result = cache.get_indicator(
            ticker="BTCUSDT",
            day=20241228,
            minute=930,
            timeframe=1,
            indicator_name="rsi",
            params={"length": 14}
        )
        
        assert result == {"rsi": 65.5}
    
    def test_indicator_cache_miss(self):
        """Test cache miss for indicators."""
        cache = ResultCache()
        
        result = cache.get_indicator(
            ticker="BTCUSDT",
            day=20241228,
            minute=930,
            timeframe=1,
            indicator_name="rsi",
            params={"length": 14}
        )
        
        assert result is None
    
    def test_indicator_cache_different_params(self):
        """Test that different params create different cache entries."""
        cache = ResultCache()
        
        # Store RSI(14)
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}, value={"rsi": 65.5}
        )
        
        # Store RSI(21)
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 21}, value={"rsi": 62.3}
        )
        
        # Retrieve RSI(14)
        result14 = cache.get_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}
        )
        
        # Retrieve RSI(21)
        result21 = cache.get_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 21}
        )
        
        assert result14 == {"rsi": 65.5}
        assert result21 == {"rsi": 62.3}
    
    def test_pattern_cache_hit(self):
        """Test cache hit for patterns."""
        cache = ResultCache()
        
        patterns = [
            {"name": "hammer", "classification": "bullish", "confidence": 0.8},
            {"name": "doji", "classification": "neutral", "confidence": 0.6}
        ]
        
        cache.set_patterns(
            ticker="BTCUSDT",
            day=20241228,
            minute=930,
            timeframe=1,
            patterns=patterns
        )
        
        result = cache.get_patterns(
            ticker="BTCUSDT",
            day=20241228,
            minute=930,
            timeframe=1
        )
        
        assert result == patterns
    
    def test_pattern_cache_miss(self):
        """Test cache miss for patterns."""
        cache = ResultCache()
        
        result = cache.get_patterns(
            ticker="BTCUSDT",
            day=20241228,
            minute=930,
            timeframe=1
        )
        
        assert result is None
    
    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = ResultCache()
        
        # Add some data
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}, value={"rsi": 65.5}
        )
        
        cache.set_patterns(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            patterns=[{"name": "hammer"}]
        )
        
        # Clear
        cache.clear()
        
        # Verify empty
        assert cache.get_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}
        ) is None
        
        assert cache.get_patterns(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1
        ) is None
    
    def test_lru_eviction(self):
        """Test that LRU eviction works."""
        cache = ResultCache(max_size_per_indicator=2)
        
        # Add 3 entries (should evict the first)
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}, value={"rsi": 65.5}
        )
        
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=931, timeframe=1,
            indicator_name="rsi", params={"length": 14}, value={"rsi": 66.0}
        )
        
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=932, timeframe=1,
            indicator_name="rsi", params={"length": 14}, value={"rsi": 66.5}
        )
        
        # First entry should be evicted
        result = cache.get_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}
        )
        assert result is None
        
        # Second and third should still be there
        result931 = cache.get_indicator(
            ticker="BTCUSDT", day=20241228, minute=931, timeframe=1,
            indicator_name="rsi", params={"length": 14}
        )
        assert result931 == {"rsi": 66.0}
        
        result932 = cache.get_indicator(
            ticker="BTCUSDT", day=20241228, minute=932, timeframe=1,
            indicator_name="rsi", params={"length": 14}
        )
        assert result932 == {"rsi": 66.5}
    
    def test_get_stats(self):
        """Test cache statistics."""
        cache = ResultCache()
        
        cache.set_indicator(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            indicator_name="rsi", params={"length": 14}, value={"rsi": 65.5}
        )
        
        cache.set_patterns(
            ticker="BTCUSDT", day=20241228, minute=930, timeframe=1,
            patterns=[{"name": "hammer"}]
        )
        
        stats = cache.get_stats()
        
        assert "indicator_caches" in stats
        assert "rsi" in stats["indicator_caches"]
        assert stats["indicator_caches"]["rsi"]["size"] == 1
        assert stats["pattern_cache"]["size"] == 1
