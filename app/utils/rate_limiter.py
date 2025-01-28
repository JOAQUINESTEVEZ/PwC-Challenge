from datetime import datetime, timedelta
from typing import Dict
import threading

class MetaSingleton(type):
    """Metaclass for ensuring singleton behavior.
    
    This metaclass ensures only one instance of a class is created.
    Uses thread-safe double-checked locking pattern.
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Check if instance exists without lock
        if cls not in cls._instances:
            # If not, acquire lock
            with cls._lock:
                # Double check once we have the lock
                if cls not in cls._instances:
                    # Create the instance
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        # Return the singleton instance
        return cls._instances[cls]
    
class RateLimitExceeded(Exception):
    """Custom exception for rate limit exceeded."""
    def __init__(self, wait_time: int):
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded. Please wait {wait_time} seconds.")

class RateLimiter(metaclass=MetaSingleton):
    """Rate limiter implementation using singleton pattern.
    
    Tracks and limits requests per user within a time window.
    Thread-safe for concurrent access.
    """
    
    def __init__(self):
        """Initialize rate limiter with default settings."""
        # Dictionary to store user request timestamps
        self.requests: Dict[str, list] = {}
        # Lock for thread-safe access to requests dict
        self._lock = threading.Lock()
        # Configure limits
        self.max_requests = 5  # Maximum requests per time window
        self.time_window = 300  # Time window in seconds (5 minutes)
    
    def check_rate_limit(self, user_id: str) -> None:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: Unique identifier for the user
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        now = datetime.now()
        
        with self._lock:
            if user_id not in self.requests:
                self.requests[user_id] = []
            
            window_start = now - timedelta(seconds=self.time_window)
            self.requests[user_id] = [
                ts for ts in self.requests[user_id] 
                if ts > window_start
            ]
            
            if len(self.requests[user_id]) >= self.max_requests:
                oldest_request = self.requests[user_id][0]
                wait_time = int(
                    (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
                )
                raise RateLimitExceeded(wait_time)
            
            self.requests[user_id].append(now)