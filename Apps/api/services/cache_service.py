"""
Simple in-memory cache for API responses
"""

import logging
from typing import Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json

logger = logging.getLogger(__name__)


class CacheService:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl_minutes: int = 30):
        """
        Initialize cache service.
        
        Args:
            default_ttl_minutes: Default time-to-live for cache entries
        """
        self.cache: dict = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        logger.info(f"✅ Cache service initialized (TTL: {default_ttl_minutes}min)")
    
    def _generate_key(self, video_id: str, query: str) -> str:
        """Generate cache key from video_id and query."""
        combined = f"{video_id}:{query}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, video_id: str, query: str) -> Optional[Any]:
        """
        Get cached response for video and query.
        
        Args:
            video_id: Video identifier
            query: User query
            
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(video_id, query)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if datetime.now() < entry['expires_at']:
                logger.info(f"✅ Cache HIT: {key[:8]}...")
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
                logger.info(f"⏰ Cache EXPIRED: {key[:8]}...")
        
        logger.info(f"❌ Cache MISS: {key[:8]}...")
        return None
    
    def set(
        self, 
        video_id: str, 
        query: str, 
        data: Any, 
        ttl_minutes: Optional[int] = None
    ) -> None:
        """
        Store response in cache.
        
        Args:
            video_id: Video identifier
            query: User query
            data: Response data to cache
            ttl_minutes: Optional custom TTL (uses default if None)
        """
        key = self._generate_key(video_id, query)
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes else self.default_ttl
        
        self.cache[key] = {
            'data': data,
            'expires_at': datetime.now() + ttl,
            'created_at': datetime.now()
        }
        
        logger.info(f"💾 Cache SET: {key[:8]}... (TTL: {ttl.total_seconds()/60:.0f}min)")
    
    def invalidate(self, video_id: str) -> None:
        """
        Invalidate all cache entries for a video.
        
        Args:
            video_id: Video identifier
        """
        keys_to_delete = []
        for key, entry in self.cache.items():
            # Check if key belongs to this video (simple prefix check)
            if key.startswith(hashlib.md5(video_id.encode()).hexdigest()[:8]):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.cache[key]
        
        if keys_to_delete:
            logger.info(f"🗑️ Invalidated {len(keys_to_delete)} cache entries for video: {video_id}")
    
    def clear(self) -> None:
        """Clear entire cache."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"🧹 Cache cleared ({count} entries removed)")
    
    def stats(self) -> dict:
        """Get cache statistics."""
        now = datetime.now()
        active = sum(1 for entry in self.cache.values() if now < entry['expires_at'])
        expired = len(self.cache) - active
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active,
            'expired_entries': expired,
            'default_ttl_minutes': self.default_ttl.total_seconds() / 60
        }


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create the cache service singleton."""
    global _cache_service
    
    if _cache_service is None:
        _cache_service = CacheService(default_ttl_minutes=30)
    
    return _cache_service


@lru_cache(maxsize=100)
def cached_query_expansion(query: str) -> list:
    """
    Expand user query with synonyms and related terms for better retrieval.
    Cached with LRU to avoid repeated processing.
    
    Args:
        query: Original user query
        
    Returns:
        List of expanded query terms
    """
    # Simple query expansion (can be enhanced with embeddings or synonym API)
    query_lower = query.lower()
    
    # Common synonyms and expansions
    expansions = {
        'explain': ['describe', 'clarify', 'elaborate'],
        'summary': ['overview', 'recap', 'summary', 'synopsis'],
        'key points': ['main points', 'highlights', 'important', 'key'],
        'tools': ['software', 'applications', 'technologies', 'platforms'],
        'how to': ['tutorial', 'guide', 'instructions', 'steps'],
    }
    
    expanded_terms = [query]
    
    for term, synonyms in expansions.items():
        if term in query_lower:
            expanded_terms.extend(synonyms)
    
    return expanded_terms
