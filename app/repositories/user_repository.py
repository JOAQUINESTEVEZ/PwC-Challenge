from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID
from ..models.user_model import User as UserModel
from ..entities.user import User

class UserRepository:
    """
    Repository for User-specific database operations.
    """
    def __init__(self, db: Session):
        """Initialize repository with db session."""
        self.db = db

    def _to_model(self, entity: User) -> UserModel:
        """Convert entity to model."""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            role_id=entity.role_id,
            client_id=entity.client_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _to_entity(self, model:UserModel) -> User:
        """Convert model to entity."""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            role_id=model.role_id,
            role=model.role,
            client_id=model.client_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def get_by_id(self, id:UUID) -> Optional[User]:
        """Get user by id."""
        model = self.db.query(UserModel).filter(UserModel.id == id).first()
        return self._to_entity(model) if model else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            Optional[User]: Found user or None
        """
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            Optional[User]: Found user or None
        """
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None
    
    async def create(self, entity: User) -> User:
        """Create a new user."""
        try:
            model = self._to_model(entity)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error creating user: {str(e)}")
        
    async def update(self, entity: User) -> User:
        """Update an existing user."""
        try:
            model = self._to_model(entity)
            self.db.merge(model)
            self.db.commit()
            
            # Refresh and return updated entity
            updated_model = self.db.query(UserModel).filter(UserModel.id == entity.id).first()
            return self._to_entity(updated_model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error updating user: {str(e)}")

    async def delete(self, id: UUID) -> None:
        """Delete a user."""
        try:
            model = self.db.query(UserModel).filter(UserModel.id == id).first()
            if model:
                self.db.delete(model)
                self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error deleting user: {str(e)}")