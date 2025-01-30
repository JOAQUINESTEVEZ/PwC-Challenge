# interfaces/repository/user_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ...entities.user import User

class IUserRepository(ABC):
    @abstractmethod
    async def create(self, entity: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        pass

    @abstractmethod
    async def update(self, entity: User) -> User:
        """Update an existing user."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a user."""
        pass