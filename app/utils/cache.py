from cachetools import TTLCache
from typing import Any, Optional
import hashlib
import json


class CacheManager:
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        data = {
            'args': args,
            'kwargs': kwargs
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value
    
    def generate_key(self, *args, **kwargs) -> str:
        return self._generate_key(*args, **kwargs)
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


# Global cache instance
cache_manager = CacheManager()