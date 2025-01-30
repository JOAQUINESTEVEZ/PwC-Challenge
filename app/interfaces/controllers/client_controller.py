# interfaces/controller/client_controller.py
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from ...schemas.request.client import ClientCreate, ClientUpdate
from ...schemas.response.client import ClientResponse
from ...entities.user import User

class IClientController(ABC):
    @abstractmethod
    async def create_client(
        self, 
        client_data: ClientCreate, 
        current_user: User
    ) -> ClientResponse:
        """Create a new client."""
        pass

    @abstractmethod
    async def get_client(
        self, 
        client_id: UUID, 
        current_user: User
    ) -> ClientResponse:
        """Get a specific client."""
        pass

    @abstractmethod
    async def get_all_clients(
        self, 
        skip: int, 
        limit: int, 
        current_user: User
    ) -> List[ClientResponse]:
        """Get all clients with pagination."""
        pass

    @abstractmethod
    async def update_client(
        self,
        client_id: UUID,
        client_data: ClientUpdate,
        current_user: User
    ) -> ClientResponse:
        """Update a client."""
        pass

    @abstractmethod
    async def delete_client(
        self,
        client_id: UUID,
        current_user: User
    ) -> None:
        """Delete a client."""
        pass

    @abstractmethod
    async def search_clients(
        self,
        search_term: str,
        current_user: User
    ) -> List[ClientResponse]:
        """Search for clients."""
        pass