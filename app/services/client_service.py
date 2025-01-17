from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.client_model import Client
from ..models.user_model import User
from ..repositories.client_repository import ClientRepository
from ..schemas.client_schema import ClientCreate, ClientUpdate
from ..models.audit_logs_model import AuditLog

class ClientService:
    """
    Service for handling client-related business logic.
    """
    
    def __init__(self, db: Session):
        self.client_repository = ClientRepository(Client, db)
        self.db = db

    def create_client(self, client_data: ClientCreate, current_user: User) -> Client:
        """
        Create a new client.
        
        Args:
            client_data: Client data to create
            current_user: Current authenticated user
            
        Returns:
            Client: Created client
        """
        # Check if client with same name exists
        existing_client = self.client_repository.get_client_by_name(client_data.name)
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Client already exists",
                    "status": 400,
                    "detail": f"Client with name '{client_data.name}' already exists",
                    "instance": "/clients"
                }
            )
            
        client = self.client_repository.create(client_data)
        
        # Create audit log
        audit_log = AuditLog(
            changed_by=current_user.id,
            table_name="clients",
            record_id=client.id,
            change_type="create",
            change_details=f"Created client {client.name}"
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return client

    def get_client(self, client_id: UUID, current_user: User) -> Client:
        """
        Get a client by ID.
        
        Args:
            client_id: UUID of client to retrieve
            current_user: Current authenticated user
            
        Returns:
            Client: Found client
            
        Raises:
            HTTPException: If client not found
        """
        client = self.client_repository.get(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Client not found",
                    "status": 404,
                    "detail": f"Client with id '{client_id}' not found",
                    "instance": f"/clients/{client_id}"
                }
            )
            
        return client

    def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Get all clients with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Client]: List of clients
        """
        return self.client_repository.get_all(skip=skip, limit=limit)

    def update_client(self, client_id: UUID, client_data: ClientUpdate, current_user: User) -> Client:
        """
        Update a client.
        
        Args:
            client_id: UUID of client to update
            client_data: Updated client data
            current_user: Current authenticated user
            
        Returns:
            Client: Updated client
            
        Raises:
            HTTPException: If client not found
        """
        client = self.get_client(client_id, current_user)
        
        # Check if new name conflicts with existing client
        if client_data.name and client_data.name != client.name:
            existing_client = self.client_repository.get_client_by_name(client_data.name)
            if existing_client:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "type": "about:blank",
                        "title": "Client name already exists",
                        "status": 400,
                        "detail": f"Client with name '{client_data.name}' already exists",
                        "instance": f"/clients/{client_id}"
                    }
                )
        
        updated_client = self.client_repository.update(client_id, client_data)
        
        # Create audit log
        audit_log = AuditLog(
            changed_by=current_user.id,
            table_name="clients",
            record_id=client_id,
            change_type="update",
            change_details=f"Updated client {client.name}"
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return updated_client

    def delete_client(self, client_id: UUID, current_user: User) -> bool:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client to delete
            current_user: Current authenticated user
            
        Returns:
            bool: True if deleted
            
        Raises:
            HTTPException: If client not found
        """
        client = self.get_client(client_id, current_user)
        result = self.client_repository.delete(client_id)
        
        if result:
            # Create audit log
            audit_log = AuditLog(
                changed_by=current_user.id,
                table_name="clients",
                record_id=client_id,
                change_type="delete",
                change_details=f"Deleted client {client.name}"
            )
            self.db.add(audit_log)
            self.db.commit()
            
        return result

    def search_clients(self, search_term: str) -> List[Client]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List[Client]: List of matching clients
        """
        return self.client_repository.search_clients(search_term)