#!/usr/bin/env python3
"""
Redis Cache Manager for LEX Performance Optimization
🔱 JAI MAHAKAAL! Enterprise-grade caching for 70% response time reduction
"""
import json
import hashlib
import logging
import time
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_sets: int = 0
    cache_errors: int = 0
    total_response_time_saved: float = 0.0
    cost_savings_usd: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def average_time_saved(self) -> float:
        """Average time saved per cached request"""
        if self.cache_hits == 0:
            return 0.0
        return self.total_response_time_saved / self.cache_hits

class CacheManager:
    """High-performance Redis cache manager for LEX AI"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback
        self.cache_stats = CacheStats()
        self.enabled = True
        
        # Cache configuration
        self.cache_config = {
            'model_responses': {
                'ttl': 3600,  # 1 hour
                'max_size': 10000,
                'cost_per_request': 0.02  # Estimated cost per OpenRouter request
            },
            'user_sessions': {
                'ttl': 7200,  # 2 hours
                'max_size': 5000,
                'cost_per_request': 0.0
            },
            'system_data': {
                'ttl': 86400,  # 24 hours
                'max_size': 1000,
                'cost_per_request': 0.0
            },
            'embeddings': {
                'ttl': 604800,  # 7 days
                'max_size': 50000,
                'cost_per_request': 0.001
            }
        }
        
        self.initialize_redis()
    
    def initialize_redis(self) -> bool:
        """Initialize Redis connection with connection pooling"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️ Redis not available - using fallback cache")
            return False
        
        try:
            # Create connection pool for high performance
            pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=50,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            self.redis_client = redis.Redis(
                connection_pool=pool,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            
            logger.info("✅ Redis cache initialized with connection pooling")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis initialization failed: {e}")
            logger.info("📝 Using in-memory fallback cache")
            return False
    
    def generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache keys"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        # Create hash for consistent key length
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        
        return f"lex:{prefix}:{data_hash}"
    
    def cache_model_response(
        self, 
        prompt: str, 
        model: str, 
        response: Dict[str, Any], 
        context: Optional[Dict] = None,
        cache_type: str = 'model_responses'
    ) -> bool:
        """Cache model response with intelligent key generation"""
        try:
            start_time = time.time()
            
            # Generate cache key from prompt + model + context
            cache_data = {
                'prompt': prompt[:1000],  # Limit prompt length for key
                'model': model,
                'context': context or {}
            }
            
            cache_key = self.generate_cache_key(cache_type, cache_data)
            
            # Prepare response data with metadata
            cache_value = {
                'response': response,
                'timestamp': datetime.utcnow().isoformat(),
                'model': model,
                'prompt_length': len(prompt),
                'context_hash': hashlib.md5(json.dumps(context or {}).encode()).hexdigest()[:8]
            }
            
            ttl = self.cache_config[cache_type]['ttl']
            
            # Cache to Redis or fallback
            if self.redis_client:
                self.redis_client.setex(cache_key, ttl, json.dumps(cache_value))
            else:
                # Fallback cache with size limits
                if len(self.fallback_cache) >= self.cache_config[cache_type]['max_size']:
                    # Remove oldest entries
                    oldest_key = min(self.fallback_cache.keys())
                    del self.fallback_cache[oldest_key]
                
                self.fallback_cache[cache_key] = {
                    'data': cache_value,
                    'expires': time.time() + ttl
                }
            
            # Update statistics
            self.cache_stats.cache_sets += 1
            cache_time = time.time() - start_time
            
            logger.debug(f"✅ Cached response for {model}: {cache_key[:20]}... ({cache_time:.3f}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache set failed: {e}")
            self.cache_stats.cache_errors += 1
            return False
    
    def get_cached_response(
        self, 
        prompt: str, 
        model: str, 
        context: Optional[Dict] = None,
        cache_type: str = 'model_responses'
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached model response"""
        try:
            start_time = time.time()
            self.cache_stats.total_requests += 1
            
            # Generate same cache key
            cache_data = {
                'prompt': prompt[:1000],
                'model': model,
                'context': context or {}
            }
            
            cache_key = self.generate_cache_key(cache_type, cache_data)
            
            cached_value = None
            
            # Try Redis first
            if self.redis_client:
                try:
                    cached_data = self.redis_client.get(cache_key)
                    if cached_data:
                        cached_value = json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"⚠️ Redis get failed: {e}")
            
            # Try fallback cache
            if not cached_value and cache_key in self.fallback_cache:
                cache_entry = self.fallback_cache[cache_key]
                
                if cache_entry['expires'] > time.time():
                    cached_value = cache_entry['data']
                else:
                    # Expired entry
                    del self.fallback_cache[cache_key]
            
            cache_time = time.time() - start_time
            
            if cached_value:
                # Cache hit!
                self.cache_stats.cache_hits += 1
                
                # Estimate time and cost savings
                estimated_api_time = 2.0  # Assume 2 seconds for API call
                time_saved = estimated_api_time - cache_time
                self.cache_stats.total_response_time_saved += max(0, time_saved)
                
                # Calculate cost savings
                cost_saved = self.cache_config[cache_type]['cost_per_request']
                self.cache_stats.cost_savings_usd += cost_saved
                
                logger.debug(f"🎯 Cache HIT for {model}: {cache_key[:20]}... (saved {time_saved:.2f}s)")
                return cached_value['response']
            else:
                # Cache miss
                self.cache_stats.cache_misses += 1
                logger.debug(f"❌ Cache MISS for {model}: {cache_key[:20]}...")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cache get failed: {e}")
            self.cache_stats.cache_errors += 1
            return None
    
    def cache_user_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Cache user session data"""
        cache_key = self.generate_cache_key('user_session', user_id)
        
        session_info = {
            'data': session_data,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }
        
        return self._set_cache_value(cache_key, session_info, 'user_sessions')
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session data"""
        cache_key = self.generate_cache_key('user_session', user_id)
        cached_data = self._get_cache_value(cache_key, 'user_sessions')
        
        if cached_data:
            return cached_data['data']
        return None
    
    def cache_embeddings(self, text: str, embeddings: List[float], model: str = "default") -> bool:
        """Cache text embeddings for semantic search"""
        cache_data = {
            'text_hash': hashlib.sha256(text.encode()).hexdigest()[:16],
            'model': model
        }
        
        cache_key = self.generate_cache_key('embeddings', cache_data)
        
        embedding_info = {
            'embeddings': embeddings,
            'text_length': len(text),
            'model': model,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self._set_cache_value(cache_key, embedding_info, 'embeddings')
    
    def get_cached_embeddings(self, text: str, model: str = "default") -> Optional[List[float]]:
        """Retrieve cached embeddings"""
        cache_data = {
            'text_hash': hashlib.sha256(text.encode()).hexdigest()[:16],
            'model': model
        }
        
        cache_key = self.generate_cache_key('embeddings', cache_data)
        cached_data = self._get_cache_value(cache_key, 'embeddings')
        
        if cached_data:
            return cached_data['embeddings']
        return None
    
    def _set_cache_value(self, cache_key: str, value: Any, cache_type: str) -> bool:
        """Internal method to set cache value"""
        try:
            ttl = self.cache_config[cache_type]['ttl']
            
            if self.redis_client:
                self.redis_client.setex(cache_key, ttl, json.dumps(value))
            else:
                self.fallback_cache[cache_key] = {
                    'data': value,
                    'expires': time.time() + ttl
                }
            
            return True
        except Exception as e:
            logger.error(f"❌ Cache set failed: {e}")
            return False
    
    def _get_cache_value(self, cache_key: str, cache_type: str) -> Optional[Any]:
        """Internal method to get cache value"""
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            
            if cache_key in self.fallback_cache:
                cache_entry = self.fallback_cache[cache_key]
                if cache_entry['expires'] > time.time():
                    return cache_entry['data']
                else:
                    del self.fallback_cache[cache_key]
            
            return None
        except Exception as e:
            logger.error(f"❌ Cache get failed: {e}")
            return None
    
    def invalidate_cache(self, pattern: str = None) -> int:
        """Invalidate cache entries matching pattern"""
        try:
            count = 0
            
            if self.redis_client and pattern:
                # Use Redis SCAN for pattern matching
                for key in self.redis_client.scan_iter(match=f"lex:{pattern}:*"):
                    self.redis_client.delete(key)
                    count += 1
            elif pattern is None:
                # Clear all cache
                if self.redis_client:
                    self.redis_client.flushdb()
                self.fallback_cache.clear()
                count = -1  # Indicates full clear
            
            logger.info(f"🗑️ Invalidated {count} cache entries")
            return count
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation failed: {e}")
            return 0
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            redis_info = {}
            
            if self.redis_client:
                try:
                    info = self.redis_client.info()
                    redis_info = {
                        'used_memory': info.get('used_memory_human', 'Unknown'),
                        'connected_clients': info.get('connected_clients', 0),
                        'total_commands_processed': info.get('total_commands_processed', 0),
                        'keyspace_hits': info.get('keyspace_hits', 0),
                        'keyspace_misses': info.get('keyspace_misses', 0)
                    }
                    
                    if redis_info['keyspace_hits'] + redis_info['keyspace_misses'] > 0:
                        redis_hit_rate = (redis_info['keyspace_hits'] / 
                                        (redis_info['keyspace_hits'] + redis_info['keyspace_misses'])) * 100
                        redis_info['hit_rate'] = f"{redis_hit_rate:.2f}%"
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not get Redis info: {e}")
            
            stats = {
                'cache_stats': asdict(self.cache_stats),
                'redis_info': redis_info,
                'fallback_cache_size': len(self.fallback_cache),
                'cache_config': self.cache_config,
                'performance_metrics': {
                    'hit_rate_percent': round(self.cache_stats.hit_rate, 2),
                    'total_cost_savings_usd': round(self.cache_stats.cost_savings_usd, 2),
                    'average_time_saved_seconds': round(self.cache_stats.average_time_saved, 3),
                    'requests_per_minute': self._calculate_requests_per_minute()
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get cache statistics: {e}")
            return {'error': str(e)}
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate approximate requests per minute"""
        # This is a simple calculation - in production you'd use a time-window approach
        if self.cache_stats.total_requests > 0:
            return self.cache_stats.total_requests / 60.0  # Rough estimate
        return 0.0
    
    def optimize_cache_performance(self) -> Dict[str, Any]:
        """Analyze and optimize cache performance"""
        stats = self.get_cache_statistics()
        recommendations = []
        
        hit_rate = self.cache_stats.hit_rate
        
        if hit_rate < 20:
            recommendations.append("Consider increasing cache TTL for frequently accessed data")
        elif hit_rate > 80:
            recommendations.append("Excellent cache performance! Consider expanding cache coverage")
        
        if self.cache_stats.cache_errors > 0:
            error_rate = (self.cache_stats.cache_errors / max(1, self.cache_stats.total_requests)) * 100
            if error_rate > 5:
                recommendations.append("High cache error rate - check Redis connection stability")
        
        if not self.redis_client:
            recommendations.append("Redis unavailable - consider installing Redis for better performance")
        
        optimization_report = {
            'current_performance': stats['performance_metrics'],
            'recommendations': recommendations,
            'estimated_improvements': {
                'potential_hit_rate': min(hit_rate + 15, 85),
                'potential_cost_savings': stats['performance_metrics']['total_cost_savings_usd'] * 1.5,
                'potential_time_savings': stats['performance_metrics']['average_time_saved_seconds'] * 1.3
            }
        }
        
        return optimization_report

# Global cache manager instance
cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    return cache_manager