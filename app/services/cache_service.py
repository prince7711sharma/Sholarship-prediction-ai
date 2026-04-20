import time
from typing import Dict, Any, Optional
from app.core.logger import get_logger
from app.schemas.student import Student

logger = get_logger("cache_service")

class ScholarshipCache:
    def __init__(self, ttl_seconds: int = 86400):  # Default 24 hours
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def _generate_key(self, data: Student) -> str:
        """
        Generate a 'bucketed' cache key.
        Groups students by similar marks (5% buckets) and income (50k buckets).
        """
        # Bucket marks: 82 -> 80, 87 -> 85
        marks_bucket = (data.marks // 5) * 5
        
        # Bucket income: 120,000 -> 100,000
        income_bucket = (data.income // 50000) * 50000
        
        # Exact match for categorical data
        key_parts = [
            str(marks_bucket),
            data.category.upper(),
            str(income_bucket),
            data.state.lower().strip(),
            data.course.lower().strip(),
            str(data.gender).lower() if data.gender else "none",
            str(data.disability).lower()
        ]
        
        return "|".join(key_parts)

    def get(self, data: Student) -> Optional[dict]:
        """Retrieve a result from cache if it exists and hasn't expired."""
        key = self._generate_key(data)
        
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self._ttl:
                logger.info(f"⚡ Cache Hit: {key}")
                return entry["data"]
            else:
                # Expired
                logger.info(f"⌛ Cache Expired: {key}")
                del self._cache[key]
        
        return None

    def set(self, data: Student, result: dict):
        """Store a result in the cache."""
        key = self._generate_key(data)
        self._cache[key] = {
            "data": result,
            "timestamp": time.time()
        }
        logger.info(f"💾 Cached result for: {key}")

# Singleton instance
scholarship_cache = ScholarshipCache()
