from abc import ABC, abstractmethod
from typing import Optional, Any, TypeVar, Generic

T = TypeVar('T')

class ICacheRepository(ABC, Generic[T]):
    """Interface for cache repository operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        pass