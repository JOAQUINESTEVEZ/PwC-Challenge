from typing import Optional
from sqlalchemy.orm import Session
from ..models.user_model import User
from ..schemas.user_schema import UserCreate, UserUpdate
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repository for User-specific database operations.
    """
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            Optional[User]: Found user or None
        """
        return self.db.query(self.model).filter(self.model.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            Optional[User]: Found user or None
        """
        return self.db.query(self.model).filter(self.model.email == email).first()