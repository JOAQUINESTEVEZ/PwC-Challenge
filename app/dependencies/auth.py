from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.user_model import User
from ..utils.jwt import verify_token
from ..repositories.user_repository import UserRepository
from ..services.permission_service import PermissionService
from ..utils.rate_limiter import RateLimiter, RateLimitExceeded

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> dict:
    """Get the current authenticated user."""
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "about:blank",
                "title": "Invalid authentication credentials",
                "status": 401,
                "detail": "User ID not found in token",
                "instance": "/auth/token"
            }
        )
    
    user_repository = UserRepository(User, db)
    user = user_repository.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "about:blank",
                "title": "Invalid authentication credentials",
                "status": 401,
                "detail": "User not found",
                "instance": "/auth/token"
            }
        )
    return user

def check_permissions(required_resource: str, required_action: str):
    """Decorator to check if the user has the required permissions."""
    async def permission_checker(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        permission_service = PermissionService(db)
        has_permission = permission_service.check_permission(
            role_id=current_user.role_id,
            resource=required_resource,
            action=required_action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "Not enough permissions",
                    "instance": f"/{required_resource}"
                }
            )
        return current_user
    return permission_checker