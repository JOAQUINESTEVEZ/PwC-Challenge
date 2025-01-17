from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..services.client_service import ClientService
from ..schemas.client_schema import Client, ClientCreate, ClientUpdate

class ClientController:
    """
    Controller handling client-related operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize ClientController with database session.
        
        Args:
            db: Database session
        """
        self.client_service = ClientService(db)

    async def create_client(self, client_data: ClientCreate, current_user: Dict[str, Any]) -> Client:
        """
        Create a new client.
        
        Args:
            client_data: Client data to create
            current_user: Current authenticated user
            
        Returns:
            Client: Created client
        """
        return self.client_service.create_client(client_data, current_user)

    async def get_client(self, client_id: UUID, current_user: Dict[str, Any]) -> Client:
        """
        Get a client by ID.
        
        Args:
            client_id: UUID of client to retrieve
            current_user: Current authenticated user
            
        Returns:
            Client: Found client
        """
        return self.client_service.get_client(client_id, current_user)

    async def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Get all clients with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Client]: List of clients
        """
        return self.client_service.get_all_clients(skip, limit)

    async def update_client(self, client_id: UUID, client_data: ClientUpdate, current_user: Dict[str, Any]) -> Client:
        """
        Update a client.
        
        Args:
            client_id: UUID of client to update
            client_data: Updated client data
            current_user: Current authenticated user
            
        Returns:
            Client: Updated client
        """
        return self.client_service.update_client(client_id, client_data, current_user)

    async def delete_client(self, client_id: UUID, current_user: Dict[str, Any]) -> bool:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client to delete
            current_user: Current authenticated user
            
        Returns:
            bool: True if deleted
        """
        return self.client_service.delete_client(client_id, current_user)

    async def search_clients(self, search_term: str) -> List[Client]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List[Client]: List of matching clients
        """
        return self.client_service.search_clients(search_term)