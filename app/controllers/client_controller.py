from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..services.client_service import ClientService
from ..schemas.client_schema import Client, ClientCreate, ClientUpdate
from ..models.user_model import User

class ClientController:
    """
    Controller handling client-related operations.
    Manages access control and coordinates between routes and services.
    """
    
    def __init__(self, db: Session):
        """
        Initialize ClientController with database session.
        
        Args:
            db: Database session
        """
        self.client_service = ClientService(db)

    def _check_client_access(self, client_id: UUID, current_user: User):
        """
        Check if user has access to client information.
        
        Args:
            client_id: UUID of client to check
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If access is denied
        """
        if current_user.role.name == "client" and str(client_id) != str(current_user.client_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "Access to this client is not allowed",
                    "instance": f"/clients/{client_id}"
                }
            )

    def _check_admin_access(self, current_user: User):
        """
        Check if user has admin role.
        
        Args:
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If user is not an admin
        """
        if current_user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "Only administrators can perform this action",
                    "instance": "/clients"
                }
            )

    async def create_client(self, client_data: ClientCreate, current_user: User) -> Client:
        """
        Create a new client.
        
        Args:
            client_data: Client data to create
            current_user: Current authenticated user
            
        Returns:
            Client: Created client
            
        Raises:
            HTTPException: If creation fails or permissions not met
        """
        try:
            return self.client_service.create_client(client_data, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": str(e),
                    "instance": "/clients"
                }
            )

    async def get_client(self, client_id: UUID, current_user: User) -> Client:
        """
        Get a client by ID.
        
        Args:
            client_id: UUID of client to retrieve
            current_user: Current authenticated user
            
        Returns:
            Client: Found client
            
        Raises:
            HTTPException: If client not found or access denied
        """
        # Check access before attempting to get client
        self._check_client_access(client_id, current_user)
        
        try:
            return self.client_service.get_client(client_id, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Not Found",
                    "status": 404,
                    "detail": str(e),
                    "instance": f"/clients/{client_id}"
                }
            )

    async def get_all_clients(self, skip: int = 0, limit: int = 100, current_user: User = None) -> List[Client]:
        """
        Get all clients with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            current_user: Current authenticated user
            
        Returns:
            List[Client]: List of clients
        """
        clients = self.client_service.get_all_clients(skip, limit)
        
        # Filter for client role
        if current_user.role.name == "client":
            clients = [c for c in clients if str(c.id) == str(current_user.client_id)]
            
        return clients

    async def update_client(self, client_id: UUID, client_data: ClientUpdate, current_user: User) -> Client:
        """
        Update a client.
        
        Args:
            client_id: UUID of client to update
            client_data: Updated client data
            current_user: Current authenticated user
            
        Returns:
            Client: Updated client
            
        Raises:
            HTTPException: If update fails or access denied
        """
        # Check access before attempting update
        self._check_client_access(client_id, current_user)
        
        try:
            return self.client_service.update_client(client_id, client_data, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": str(e),
                    "instance": f"/clients/{client_id}"
                }
            )

    async def delete_client(self, client_id: UUID, current_user: User) -> bool:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client to delete
            current_user: Current authenticated user
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            HTTPException: If deletion fails or access denied
        """
        # Check admin access for deletion
        self._check_admin_access(current_user)
        
        try:
            return self.client_service.delete_client(client_id, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": str(e),
                    "instance": f"/clients/{client_id}"
                }
            )

    async def search_clients(self, search_term: str, current_user: User) -> List[Client]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            current_user: Current authenticated user
            
        Returns:
            List[Client]: List of matching clients
        """
        clients = self.client_service.search_clients(search_term)
        
        # Filter for client role
        if current_user.role.name == "client":
            clients = [c for c in clients if str(c.id) == str(current_user.client_id)]
            
        return clients