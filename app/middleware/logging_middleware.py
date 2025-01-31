import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ..utils.logging import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Get status code and path
        status_code = response.status_code
        path = request.url.path

        # Determine message based on status code
        if status_code >= 500:
            level = "ERROR"
            msg = "Server error occurred"
        elif status_code >= 400:
            level = "WARNING"
            msg = "Client error occurred"
        else:
            level = "INFO"
            msg = "Request completed successfully"

        # Log with extra context
        extra = {
            'method': request.method,
            'url': path,
            'status': status_code,
            'duration': duration,
        }

        # Log at appropriate level
        if level == "ERROR":
            logger.error(msg, extra=extra)
        elif level == "WARNING":
            logger.warning(msg, extra=extra)
        else:
            logger.info(msg, extra=extra)

        return response