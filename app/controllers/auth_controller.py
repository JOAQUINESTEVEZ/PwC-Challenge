from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..services.auth_service import AuthService
from ..schemas.request.login import LoginRequest
from ..schemas.request.signup import SignupRequest
from ..schemas.response.login import LoginResponse
from ..schemas.dto.user_dto import UserDTO
from ..schemas.dto.client_dto import ClientDTO
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
        result = await self.auth_service.authenticate_user(
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
        try:
            # Convert Request to DTO
            client_dto = ClientDTO(
                id=None,
                name=signup_data.company_name,
                industry=signup_data.industry,
                contact_email=signup_data.contact_email,
                contact_phone=signup_data.contact_phone,
                address=signup_data.address
            )
            user_dto = UserDTO(
                id=None,
                username=signup_data.username,
                email=signup_data.email,
                password_hash=signup_data.password, # will hash password in service
                role_id=None,
                client_id=None,
            )

            return await self.auth_service.signup_client(client_dto, user_dto)
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid transaction data",
                    "status": 400,
                    "detail": str(e),
                    "instance": "/finance/transactions"
                }
            )

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