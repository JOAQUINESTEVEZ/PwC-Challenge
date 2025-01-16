from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..repositories.user_repository import UserRepository
from ..models.user_model import User
from ..schemas.auth_schema import LoginResponse
from ..utils.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Service for handling authentication-related business logic.
    """
    
    def __init__(self, db: Session):
        self.user_repository = UserRepository(User, db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Password in plain text
            hashed_password: Hashed password to compare against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[LoginResponse]:
        """
        Authenticate a user and generate access token.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Optional[LoginResponse]: Login response with token if successful, None otherwise
        """
        user = self.user_repository.get_by_username(username)
        if not user or not self.verify_password(password, user.password_hash):
            return None
            
        # Transform user data for token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.name if user.role else None
        }
        
        access_token = create_access_token(token_data)
        return LoginResponse(access_token=access_token, token_type="bearer")