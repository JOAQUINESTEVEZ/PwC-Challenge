from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from ...entities.client import Client

class IClientRepository(ABC):
    @abstractmethod
    async def create(self, entity: Client) -> Client:
        """Create a new client."""
        pass
    
    @abstractmethod
    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get a client by ID."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get all clients with pagination."""
        pass
    
    @abstractmethod
    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """Get a client by name."""
        pass

    @abstractmethod
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """Get a client by email."""
        pass

    @abstractmethod
    async def get_clients_by_industry(self, industry: str) -> List[Client]:
        """Get a client by industry."""
        pass
    
    @abstractmethod
    async def search_clients(self, search_term: str) -> List[Client]:
        """Search clients by name or industry."""
        pass

    @abstractmethod
    async def update(self, entity: Client) -> Client:
        """Update an existing client."""
        pass
    
    @abstractmethod
    async def delete(self, client_id: UUID) -> None:
        """Delete a client."""
        pass