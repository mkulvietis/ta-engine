from typing import Any, Dict, Optional, List
from threading import Lock
from cachetools import LRUCache


def _make_params_key(params: Dict[str, Any]) -> frozenset:
    """
    Create a hashable cache key from indicator parameters.
    
    Optimized for performance:
    - Uses frozenset instead of JSON serialization
    - Works because indicator params are always flat dicts with primitive values
    - ~10x faster than JSON+MD5 approach
    
    Args:
        params: Flat dictionary with primitive values (int, float, str, bool)
        
    Returns:
        Frozenset of (key, value) tuples that can be used as dict key
    """
    if not params:
        return frozenset()
    return frozenset(params.items())


class ResultCache:
    """
    L1 cache for computed indicator and pattern results.
    Only caches results for bars with is_final=True.
    """
    
    def __init__(self, max_size_per_indicator: int = 1000, max_size_patterns: int = 2000):
        """
        Initialize the result cache.
        
        Args:
            max_size_per_indicator: Max entries per indicator cache (LRU eviction)
            max_size_patterns: Max entries for pattern cache
        """
        self._indicator_caches: Dict[str, LRUCache] = {}
        self._pattern_cache: LRUCache = LRUCache(maxsize=max_size_patterns)
        self._lock = Lock()
        self._max_size_per_indicator = max_size_per_indicator
    
    def _get_indicator_cache(self, indicator_name: str) -> LRUCache:
        """Get or create cache for a specific indicator."""
        if indicator_name not in self._indicator_caches:
            self._indicator_caches[indicator_name] = LRUCache(maxsize=self._max_size_per_indicator)
        return self._indicator_caches[indicator_name]
    
    def get_indicator(
        self,
        ticker: str,
        day: int,
        minute: int,
        timeframe: int,
        indicator_name: str,
        params: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Retrieve cached indicator result.
        
        Returns:
            Cached result or None if not found
        """
        params_key = _make_params_key(params)
        cache_key = (ticker, day, minute, timeframe, params_key)
        
        with self._lock:
            cache = self._get_indicator_cache(indicator_name)
            return cache.get(cache_key)
    
    def set_indicator(
        self,
        ticker: str,
        day: int,
        minute: int,
        timeframe: int,
        indicator_name: str,
        params: Dict[str, Any],
        value: Any
    ):
        """
        Store indicator result in cache.
        Should only be called for bars with is_final=True.
        """
        params_key = _make_params_key(params)
        cache_key = (ticker, day, minute, timeframe, params_key)
        
        with self._lock:
            cache = self._get_indicator_cache(indicator_name)
            cache[cache_key] = value
    
    def get_patterns(
        self,
        ticker: str,
        day: int,
        minute: int,
        timeframe: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached pattern detection results.
        
        Returns:
            List of detected patterns or None if not found
        """
        cache_key = (ticker, day, minute, timeframe)
        
        with self._lock:
            return self._pattern_cache.get(cache_key)
    
    def set_patterns(
        self,
        ticker: str,
        day: int,
        minute: int,
        timeframe: int,
        patterns: List[Dict[str, Any]]
    ):
        """
        Store pattern detection results in cache.
        Should only be called for bars with is_final=True.
        """
        cache_key = (ticker, day, minute, timeframe)
        
        with self._lock:
            self._pattern_cache[cache_key] = patterns
    
    def clear(self):
        """Clear all caches."""
        with self._lock:
            self._indicator_caches.clear()
            self._pattern_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        with self._lock:
            return {
                "indicator_caches": {
                    name: {
                        "size": len(cache),
                        "maxsize": cache.maxsize
                    }
                    for name, cache in self._indicator_caches.items()
                },
                "pattern_cache": {
                    "size": len(self._pattern_cache),
                    "maxsize": self._pattern_cache.maxsize
                }
            }


# Global cache instance
global_cache = ResultCache()
