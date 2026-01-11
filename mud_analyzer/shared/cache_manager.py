#!/usr/bin/env python3
"""
Cache Manager - Optimized caching for MUD Analyzer
"""

import pickle
import time
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple
from mud_analyzer.shared.config import config


class CacheManager:
    """Manages caching for improved performance"""
    
    def __init__(self):
        self.memory_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
    
    def get_cache_file_path(self, cache_name: str) -> Path:
        """Get the path to a cache file"""
        return config.get_cache_file(cache_name)
    
    def is_cache_valid(self, cache_name: str, max_age_seconds: int = None) -> bool:
        """Check if cache is still valid"""
        if max_age_seconds is None:
            max_age_seconds = config.cache_validity_seconds
        
        # Check disk cache first for timestamp
        cache_file = self.get_cache_file_path(cache_name)
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                timestamp = cache_data.get('timestamp', 0)
                age = time.time() - timestamp
                return age < max_age_seconds
        except Exception:
            return False
    
    def load_from_cache(self, cache_name: str) -> Optional[Any]:
        """Load data from cache (disk first for persistence, then memory)"""
        # Try disk cache first for persistence between executions
        cache_file = self.get_cache_file_path(cache_name)
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if self.is_cache_valid(cache_name):
                        data = cache_data['data']
                        # Store in memory cache for faster access
                        self.memory_cache[cache_name] = data
                        self.cache_timestamps[cache_name] = cache_data['timestamp']
                        return data
            except Exception:
                pass
        
        # Fallback to memory cache if disk cache fails
        if cache_name in self.memory_cache and cache_name in self.cache_timestamps:
            return self.memory_cache[cache_name]
        
        return None
    
    def save_to_cache(self, cache_name: str, data: Any) -> bool:
        """Save data to cache (both memory and disk)"""
        try:
            timestamp = time.time()
            
            # Save to memory cache
            self.memory_cache[cache_name] = data
            self.cache_timestamps[cache_name] = timestamp
            
            # Ensure cache directory exists
            config.cache_dir.mkdir(exist_ok=True)
            
            # Save to disk cache
            cache_data = {
                'timestamp': timestamp,
                'data': data
            }
            cache_file = self.get_cache_file_path(cache_name)
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            return True
        except Exception as e:
            print(f"Warning: Failed to save cache {cache_name}: {e}")
            return False
    
    def clear_cache(self, cache_name: str = None) -> None:
        """Clear cache (specific cache or all caches)"""
        if cache_name:
            # Clear specific cache
            self.memory_cache.pop(cache_name, None)
            self.cache_timestamps.pop(cache_name, None)
            cache_file = self.get_cache_file_path(cache_name)
            cache_file.unlink(missing_ok=True)
        else:
            # Clear all caches
            self.memory_cache.clear()
            self.cache_timestamps.clear()
            for cache_file in config.cache_dir.glob("*.pkl"):
                cache_file.unlink(missing_ok=True)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'memory_caches': len(self.memory_cache),
            'disk_caches': len(list(config.cache_dir.glob("*.pkl"))),
            'cache_dir_size': sum(f.stat().st_size for f in config.cache_dir.glob("*.pkl"))
        }
        return stats


# Global cache manager instance
cache_manager = CacheManager()