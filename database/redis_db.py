"""Redis database connection and operations."""
import redis
import json
from typing import Optional, Any, Dict
from datetime import datetime, date
from decimal import Decimal
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and Decimal objects."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class RedisDB:
    """Redis handler for caching and session management."""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True
        )
        try:
            self.client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def set_cache(self, key: str, value: Any, ttl: int = 3600):
        """Set cache value with TTL."""
        try:
            if isinstance(value, str):
                serialized = value
            else:
                # Use custom encoder to handle datetime and Decimal
                serialized = json.dumps(value, cls=CustomJSONEncoder)
            self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value."""
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def delete_cache(self, key: str):
        """Delete cache key."""
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
    
    def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 7200):
        """Store session data."""
        self.set_cache(f"session:{session_id}", data, ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        return self.get_cache(f"session:{session_id}")

