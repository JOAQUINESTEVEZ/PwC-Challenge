# interfaces/service/client_service.py
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from ...schemas.dto.client_dto import ClientDTO
from ...entities.user import User

class IClientService(ABC):
    @abstractmethod
    async def create_client(self, client_dto: ClientDTO, created_by: User) -> ClientDTO:
        """Create a new client."""
        pass

    @abstractmethod
    async def get_client(self, client_id: UUID) -> ClientDTO:
        """Get a client by ID."""
        pass

    @abstractmethod
    async def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[ClientDTO]:
        """Get all clients with pagination."""
        pass
    
    @abstractmethod
    async def search_clients(self, search_term: str) -> List[ClientDTO]:
        """Search clients by name or industry"""
        pass
    
    @abstractmethod
    async def update_client(self, client_data: ClientDTO, updated_by: User) -> ClientDTO:
        """Update a client."""
        pass

    @abstractmethod
    async def delete_client(self, client_id: UUID, deleted_by: User) -> None:
        """Delete a client."""
        pass