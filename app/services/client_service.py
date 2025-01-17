from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.client_model import Client
from ..models.user_model import User
from ..repositories.client_repository import ClientRepository
from ..schemas.client_schema import ClientCreate, ClientUpdate
from ..models.audit_logs_model import AuditLog
from datetime import datetime, UTC

class ClientService:
    """
    Service for handling client-related business logic.
    Handles data operations, validations, and business rules.
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: Database session
        """
        self.client_repository = ClientRepository(Client, db)
        self.db = db

    def _create_audit_log(self, user_id: UUID, record_id: UUID, change_type: str, details: str) -> None:
        """
        Create an audit log entry.
        
        Args:
            user_id: ID of user making the change
            record_id: ID of affected record
            change_type: Type of change (create, update, delete)
            details: Change details
        """
        audit_log = AuditLog(
            changed_by=user_id,
            table_name="clients",
            record_id=record_id,
            change_type=change_type,
            change_details=details,
            timestamp=datetime.now(UTC)
        )
        self.db.add(audit_log)
        self.db.commit()

    def create_client(self, client_data: ClientCreate, created_by: User) -> Client:
        """
        Create a new client.
        
        Args:
            client_data: Client data for creation
            created_by: User creating the client
            
        Returns:
            Client: Created client record
            
        Raises:
            ValueError: If client with same name exists
        """
        # Business validation
        existing_client = self.client_repository.get_client_by_name(client_data.name)
        if existing_client:
            raise ValueError(f"Client with name '{client_data.name}' already exists")
            
        # Create client
        client = self.client_repository.create(client_data)
        
        # Audit logging
        self._create_audit_log(
            user_id=created_by.id,
            record_id=client.id,
            change_type="create",
            details=f"Created client {client.name}"
        )
        
        return client

    def get_client(self, client_id: UUID, _current_user: User = None) -> Client:
        """
        Get a client by ID.
        
        Args:
            client_id: UUID of client to retrieve
            _current_user: User requesting the client (unused, kept for interface consistency)
            
        Returns:
            Client: Found client
            
        Raises:
            ValueError: If client not found
        """
        client = self.client_repository.get(client_id)
        if not client:
            raise ValueError(f"Client with id '{client_id}' not found")
            
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

    def update_client(self, client_id: UUID, client_data: ClientUpdate, updated_by: User) -> Client:
        """
        Update a client.
        
        Args:
            client_id: UUID of client to update
            client_data: Updated client data
            updated_by: User performing the update
            
        Returns:
            Client: Updated client
            
        Raises:
            ValueError: If client not found or name conflict exists
        """
        # Check if client exists
        client = self.get_client(client_id)
        
        # Business validation for name changes
        if client_data.name and client_data.name != client.name:
            existing_client = self.client_repository.get_client_by_name(client_data.name)
            if existing_client:
                raise ValueError(f"Client with name '{client_data.name}' already exists")
        
        # Update client
        updated_client = self.client_repository.update(client_id, client_data)
        
        # Audit logging
        self._create_audit_log(
            user_id=updated_by.id,
            record_id=client_id,
            change_type="update",
            details=f"Updated client {client.name}"
        )
        
        return updated_client

    def delete_client(self, client_id: UUID, deleted_by: User) -> bool:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client to delete
            deleted_by: User performing the deletion
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            ValueError: If client has active transactions or invoices
        """
        # Check if client exists
        client = self.get_client(client_id)
        
        # Perform deletion
        result = self.client_repository.delete(client_id)
        
        if result:
            # Audit logging
            self._create_audit_log(
                user_id=deleted_by.id,
                record_id=client_id,
                change_type="delete",
                details=f"Deleted client {client.name}"
            )
            
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