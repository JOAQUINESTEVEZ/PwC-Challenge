from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..services.auth_service import AuthService
from ..schemas.auth_schema import LoginResponse
from ..schemas.signup_schema import SignupRequest
from ..dependencies.auth import get_current_user

class AuthController:
    """
    Controller handling authentication-related business logic.
    """
    
    def __init__(self, db: Session):
        """
        Initialize AuthController with database session.
        
        Args:
            db: Database session
        """
        self.auth_service = AuthService(db)

    async def login(self, form_data: OAuth2PasswordRequestForm) -> LoginResponse:
        """
        Handle user authentication and token generation.
        
        Args:
            form_data: OAuth2 form containing username and password
            
        Returns:
            LoginResponse: Response containing access token
            
        Raises:
            HTTPException: If authentication fails
        """
        result = self.auth_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "type": "about:blank",
                    "title": "Authentication failed",
                    "status": 401,
                    "detail": "Incorrect username or password",
                    "instance": "/auth/login"
                }
            )
        
        return result
    
    async def signup(self, signup_data: SignupRequest) -> LoginResponse:
        """Handle client signup process."""
        return self.auth_service.signup_client(signup_data)

    async def get_current_user_info(self, current_user: dict) -> Dict[str, Any]:
        """
        Get current user information in API format.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Dict[str, Any]: Formatted user information
        """
        return {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role.name if current_user.role else None,
            "permissions": [
                {
                    "resource": perm.resource,
                    "action": perm.action
                }
                for perm in current_user.role.permissions
            ] if current_user.role else []
        }