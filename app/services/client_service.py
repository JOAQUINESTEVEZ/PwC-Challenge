from typing import List
from uuid import UUID
from datetime import datetime, UTC

from ..interfaces.services.client_service import IClientService
from ..interfaces.services.audit_service import IAuditService
from ..interfaces.repositories.client_repository import IClientRepository
from ..schemas.dto.client_dto import ClientDTO
from ..entities.user import User
from ..entities.client import Client

class ClientService(IClientService):
    """
    Service for handling client-related business logic.
    Handles data operations, validations, and business rules.
    """
    
    def __init__(self, client_repository: IClientRepository, audit_service: IAuditService):
        """
        Initialize service with database session.
        
        Args:
            db: Database session
        """
        self.client_repository = client_repository
        self.audit_service = audit_service

    async def create_client(self, client_dto: ClientDTO, created_by: User) -> ClientDTO:
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
        try:
            # Business validation
            existing_name = await self.client_repository.get_client_by_name(client_dto.name)
            if existing_name:
                raise ValueError(f"Client with name '{client_dto.name}' already exists")
            existing_email = await self.client_repository.get_client_by_email(client_dto.contact_email)
            if existing_email:
                raise ValueError(f"Client with email '{client_dto.contact_email}' already exists")
                
            # Convert DTO to entity
            client = Client(
                id = None,
                name=client_dto.name,
                industry=client_dto.industry,
                contact_email=client_dto.contact_email,
                contact_phone=client_dto.contact_phone,
                address=client_dto.address,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

            # Save through repository
            saved_client = await self.client_repository.create(client)

            # Create Log
            await self.audit_service.log_change(
                user_id=created_by.id,
                record_id=saved_client.id,
                table_name="clients",
                change_type="CREATE",
                details=f"Created client {saved_client.name}"
            )

            # Convert entity to DTO and return
            return ClientDTO.from_entity(saved_client)

        except Exception as e:
            raise ValueError(f"Error creating invoice: {str(e)}")

    async def get_client(self, client_id: UUID) -> ClientDTO:
        """
        Get a client by ID.
        
        Args:
            client_id: UUID of client to retrieve
            _current_user: User requesting the client (unused, kept for interface consistency)
            
        Returns:
            ClientDTO: Found client
            
        Raises:
            ValueError: If client not found
        """
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with id '{client_id}' not found")
            
        return ClientDTO.from_entity(client)

    async def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[ClientDTO]:
        """
        Get all clients with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Client]: List of clients
        """
        clients = await self.client_repository.get_all(skip=skip, limit=limit)
        return [
            ClientDTO.from_entity(client)
            for client in clients
        ]

    async def update_client(self, client_data: ClientDTO, updated_by: User) -> ClientDTO:
        """
        Update a client.
        
        Args:
            client_id: UUID of client to update
            client_data: Updated client data
            updated_by: User performing the update
            
        Returns:
            ClientDTO: Updated client
            
        Raises:
            ValueError: If client not found or name conflict exists
        """
        try:
            # Get existing client
            existing_client = await self.client_repository.get_by_id(client_data.id)
            if not existing_client:
                raise ValueError(f"Client with id '{client_data.id}' not found")
        
            # Business validation for name changes
            if client_data.name and client_data.name != existing_client.name:
                same_name = await self.client_repository.get_client_by_name(client_data.name)
                if same_name:
                    raise ValueError(f"Client with name '{client_data.name}' already exists")
            
            # Update fields while preserving others
            if client_data.name:
                existing_client.name = client_data.name
            if client_data.industry:
                existing_client.industry = client_data.industry
            if client_data.address:
                existing_client.address = client_data.address
            if client_data.contact_email:
                existing_client.contact_email = client_data.contact_email
            if client_data.contact_phone:
                existing_client.contact_phone = client_data.contact_phone
            
            existing_client.updated_at = datetime.now(UTC)

            # Save updates
            updated_client = await self.client_repository.update(existing_client)

            # Create Log
            await self.audit_service.log_change(
                user_id=updated_by.id,
                record_id=updated_client.id,
                table_name="clients",
                change_type="UPDATE",
                details=f"Updated client {updated_client.name}"
            )

            # Convert entity to DTO and return
            return ClientDTO.from_entity(updated_client)
        
        except Exception as e:
            raise ValueError(f"Error updating client: {str(e)}")

    async def delete_client(self, client_id: UUID, deleted_by: User) -> None:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client to delete
            deleted_by: User performing the deletion
            
        Returns:
            None
            
        Raises:
            ValueError: If client has active transactions or invoices
        """
        # Check if client exists
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        await self.client_repository.delete(client_id)
        
        # Create Log
        await self.audit_service.log_change(
            user_id=deleted_by.id,
            record_id=client_id,
            table_name="clients",
            change_type="DELETE",
            details=f"Deleted client {client.name}"
        )

    async def search_clients(self, search_term: str) -> List[ClientDTO]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List[ClientDTO]: List of matching clients
        """
        clients = await self.client_repository.search_clients(search_term)
        return [ClientDTO.from_entity(client) for client in clients]