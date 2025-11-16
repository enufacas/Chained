#!/usr/bin/env python3
"""
Metrics Cache Manager - Persistent Caching for Agent Metrics

This module provides a persistent caching layer for GitHub API data and agent metrics,
dramatically reducing API calls and improving performance during concurrent operations.

Architecture:
- File-based persistent cache with TTL support
- Thread-safe operations with file locking
- Automatic cleanup of expired entries
- Optimized for concurrent workflow execution

Design Philosophy (@engineer-master):
- Minimize API calls through intelligent caching
- Support concurrent access without data corruption
- Provide graceful degradation when cache misses
- Maintain data freshness with configurable TTL

Usage:
    from metrics_cache import MetricsCache
    
    cache = MetricsCache()
    
    # Cache API response
    cache.set('issue_123', issue_data, ttl_hours=1)
    
    # Retrieve from cache
    data = cache.get('issue_123')
    
    # Batch operations
    cache.set_batch({'issue_123': data1, 'issue_456': data2})
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import fcntl
from contextlib import contextmanager
import hashlib


class MetricsCache:
    """
    Persistent cache manager for agent metrics and GitHub API data.
    
    Features:
    - File-based storage for persistence across workflow runs
    - TTL (time-to-live) support for automatic expiration
    - Thread-safe operations with file locking
    - Namespace support for different data types
    - Automatic cleanup of expired entries
    """
    
    def __init__(
        self,
        cache_dir: str = ".github/agent-system/cache",
        default_ttl_hours: int = 24
    ):
        """
        Initialize metrics cache.
        
        Args:
            cache_dir: Directory for cache storage
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl_hours = default_ttl_hours
        
        # Create cache directory structure
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories for different data types
        self.issues_cache = self.cache_dir / "issues"
        self.prs_cache = self.cache_dir / "prs"
        self.timelines_cache = self.cache_dir / "timelines"
        self.metrics_cache = self.cache_dir / "metrics"
        self.api_calls_cache = self.cache_dir / "api_calls"
        
        for cache_subdir in [self.issues_cache, self.prs_cache, 
                             self.timelines_cache, self.metrics_cache,
                             self.api_calls_cache]:
            cache_subdir.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def _lock_file(self, filepath: Path):
        """Context manager for file locking"""
        lock_file = filepath.parent / f".{filepath.name}.lock"
        lock_file.touch(exist_ok=True)
        
        with open(lock_file, 'w') as f:
            # Try to acquire lock with timeout
            max_retries = 10
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    try:
                        yield
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    return
                except IOError:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise
    
    def _get_cache_path(self, namespace: str, key: str) -> Path:
        """
        Get cache file path for a key in a namespace.
        
        Args:
            namespace: Cache namespace (issues, prs, metrics, etc.)
            key: Cache key
            
        Returns:
            Path to cache file
        """
        # Hash the key to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        namespace_map = {
            'issues': self.issues_cache,
            'prs': self.prs_cache,
            'timelines': self.timelines_cache,
            'metrics': self.metrics_cache,
            'api_calls': self.api_calls_cache
        }
        
        base_dir = namespace_map.get(namespace, self.cache_dir)
        return base_dir / f"{key_hash}.json"
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            cache_entry: Cache entry with 'expires_at' field
            
        Returns:
            True if expired, False otherwise
        """
        expires_at_str = cache_entry.get('expires_at')
        if not expires_at_str:
            return True
        
        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            return datetime.now(timezone.utc) >= expires_at
        except (ValueError, AttributeError):
            return True
    
    def get(
        self,
        namespace: str,
        key: str,
        default: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            default: Default value if not found or expired
            
        Returns:
            Cached value or default
        """
        cache_path = self._get_cache_path(namespace, key)
        
        if not cache_path.exists():
            return default
        
        try:
            with self._lock_file(cache_path):
                with open(cache_path, 'r') as f:
                    cache_entry = json.load(f)
                
                if self._is_expired(cache_entry):
                    # Clean up expired entry
                    try:
                        cache_path.unlink()
                    except OSError:
                        pass
                    return default
                
                return cache_entry.get('data', default)
        except (json.JSONDecodeError, IOError):
            return default
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl_hours: Time-to-live in hours (None uses default)
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(namespace, key)
        ttl_hours = ttl_hours or self.default_ttl_hours
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        
        cache_entry = {
            'data': value,
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': expires_at.isoformat(),
            'ttl_hours': ttl_hours
        }
        
        try:
            with self._lock_file(cache_path):
                with open(cache_path, 'w') as f:
                    json.dump(cache_entry, f, indent=2)
            return True
        except (IOError, TypeError):
            return False
    
    def set_batch(
        self,
        namespace: str,
        items: Dict[str, Any],
        ttl_hours: Optional[int] = None
    ) -> int:
        """
        Set multiple values in cache (batch operation).
        
        Args:
            namespace: Cache namespace
            items: Dictionary of key-value pairs
            ttl_hours: Time-to-live in hours (None uses default)
            
        Returns:
            Number of successfully cached items
        """
        success_count = 0
        for key, value in items.items():
            if self.set(namespace, key, value, ttl_hours):
                success_count += 1
        return success_count
    
    def get_batch(
        self,
        namespace: str,
        keys: List[str]
    ) -> Dict[str, Any]:
        """
        Get multiple values from cache (batch operation).
        
        Args:
            namespace: Cache namespace
            keys: List of cache keys
            
        Returns:
            Dictionary of found key-value pairs
        """
        results = {}
        for key in keys:
            value = self.get(namespace, key)
            if value is not None:
                results[key] = value
        return results
    
    def delete(self, namespace: str, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_path = self._get_cache_path(namespace, key)
        
        if not cache_path.exists():
            return False
        
        try:
            cache_path.unlink()
            return True
        except OSError:
            return False
    
    def cleanup_expired(self, namespace: Optional[str] = None) -> int:
        """
        Clean up expired cache entries.
        
        Args:
            namespace: Optional namespace to clean (None cleans all)
            
        Returns:
            Number of entries cleaned up
        """
        cleaned_count = 0
        
        if namespace:
            cache_dirs = [self._get_cache_path(namespace, '').parent]
        else:
            cache_dirs = [
                self.issues_cache,
                self.prs_cache,
                self.timelines_cache,
                self.metrics_cache,
                self.api_calls_cache
            ]
        
        for cache_dir in cache_dirs:
            if not cache_dir.exists():
                continue
            
            for cache_file in cache_dir.glob("*.json"):
                try:
                    with self._lock_file(cache_file):
                        with open(cache_file, 'r') as f:
                            cache_entry = json.load(f)
                        
                        if self._is_expired(cache_entry):
                            cache_file.unlink()
                            cleaned_count += 1
                except (json.JSONDecodeError, IOError, OSError):
                    # If we can't read or delete, skip it
                    pass
        
        return cleaned_count
    
    def clear(self, namespace: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            namespace: Optional namespace to clear (None clears all)
            
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        
        if namespace:
            cache_dirs = [self._get_cache_path(namespace, '').parent]
        else:
            cache_dirs = [
                self.issues_cache,
                self.prs_cache,
                self.timelines_cache,
                self.metrics_cache,
                self.api_calls_cache
            ]
        
        for cache_dir in cache_dirs:
            if not cache_dir.exists():
                continue
            
            for cache_file in cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except OSError:
                    pass
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'namespaces': {},
            'total_entries': 0,
            'total_size_bytes': 0
        }
        
        for namespace in ['issues', 'prs', 'timelines', 'metrics', 'api_calls']:
            cache_dir = self._get_cache_path(namespace, '').parent
            
            if not cache_dir.exists():
                continue
            
            entries = list(cache_dir.glob("*.json"))
            size = sum(f.stat().st_size for f in entries if f.is_file())
            
            stats['namespaces'][namespace] = {
                'entries': len(entries),
                'size_bytes': size
            }
            stats['total_entries'] += len(entries)
            stats['total_size_bytes'] += size
        
        return stats


if __name__ == '__main__':
    # Simple CLI for cache management
    import sys
    
    cache = MetricsCache()
    
    if len(sys.argv) < 2:
        print("Usage: python metrics_cache.py <command> [args]")
        print("Commands:")
        print("  stats                 - Show cache statistics")
        print("  cleanup [namespace]   - Clean up expired entries")
        print("  clear [namespace]     - Clear all entries")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'stats':
        stats = cache.get_stats()
        print(f"Cache Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Total size: {stats['total_size_bytes'] / 1024:.2f} KB")
        print(f"\nNamespaces:")
        for ns, ns_stats in stats['namespaces'].items():
            print(f"  {ns}:")
            print(f"    Entries: {ns_stats['entries']}")
            print(f"    Size: {ns_stats['size_bytes'] / 1024:.2f} KB")
    
    elif command == 'cleanup':
        namespace = sys.argv[2] if len(sys.argv) > 2 else None
        cleaned = cache.cleanup_expired(namespace)
        print(f"Cleaned up {cleaned} expired cache entries")
    
    elif command == 'clear':
        namespace = sys.argv[2] if len(sys.argv) > 2 else None
        cleared = cache.clear(namespace)
        print(f"Cleared {cleared} cache entries")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
