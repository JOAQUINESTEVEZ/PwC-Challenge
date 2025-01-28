from fastapi import HTTPException, status, Depends
from ..models.user_model import User
from ..utils.rate_limiter import RateLimiter, RateLimitExceeded
from .auth import get_current_user

def check_user_pdf_rate_limit(
    current_user: User = Depends(get_current_user)
) -> None:
    """
    FastAPI dependency that checks PDF rate limit for current user.
    
    Args:
        current_user: Current authenticated user (injected by FastAPI)
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    rate_limiter = RateLimiter()
    
    try:
        rate_limiter.check_rate_limit(str(current_user.id))
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "type": "about:blank",
                "title": "Too Many Requests",
                "status": 429,
                "detail": f"Rate limit exceeded for PDF generation. Please try again in {e.wait_time} seconds.",
                "instance": "/clients/{client_id}/report"
            }
        )