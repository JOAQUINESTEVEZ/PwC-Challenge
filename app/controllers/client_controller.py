from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..services.client_service import ClientService
from ..schemas.request.client import ClientCreate, ClientUpdate
from ..schemas.response.client import ClientResponse
from ..schemas.dto.client_dto import ClientDTO
from ..entities.client import Client
from ..entities.user import User

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

    async def create_client(self, client_data: ClientCreate, current_user: User) -> ClientResponse:
        """
        Create a new client.
        
        Args:
            client_data: ClientCreate data to create
            current_user: Current authenticated user
            
        Returns:
            ClientResponse: Created client
            
        Raises:
            HTTPException: If creation fails or permissions not met
        """
        try:
            # Convert Request to DTO
            client_dto = ClientDTO(
                id = None,
                name = client_data.name,
                industry= client_data.industry,
                contact_email= client_data.contact_email,
                contact_phone= client_data.contact_phone,
                address = client_data.address
            )

            # Send DTO to service, get DTO back
            result_dto = await self.client_service.create_client(client_dto, current_user)

            # Convert DTO to Response
            return ClientResponse(
                id = result_dto.id,
                name = result_dto.name,
                industry = result_dto.industry,
                contact_email = result_dto.contact_email,
                contact_phone = result_dto.contact_phone,
                address = result_dto.address
            )
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

    async def get_client(self, client_id: UUID, current_user: User) -> ClientResponse:
        """
        Get a client by ID.
        
        Args:
            client_id: UUID of client to retrieve
            current_user: Current authenticated user
            
        Returns:
            ClientResponse: Found client
            
        Raises:
            HTTPException: If client not found or access denied
        """
        # Check access before attempting to get client
        self._check_client_access(client_id, current_user)
        
        try:
            result_dto = await self.client_service.get_client(client_id)

            # Convert DTO to Response
            return ClientResponse(
                id = result_dto.id,
                name = result_dto.name,
                industry = result_dto.industry,
                contact_email = result_dto.contact_email,
                contact_phone = result_dto.contact_phone,
                address = result_dto.address
            )

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

    async def get_all_clients(self, skip: int = 0, limit: int = 100, current_user: User = None) -> List[ClientResponse]:
        """
        Get all clients with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            current_user: Current authenticated user
            
        Returns:
            List[ClientResponse]: List of clients
        """
        client_dtos = await self.client_service.get_all_clients(skip, limit)
        
        # Filter for client role
        if current_user.role.name == "client":
            client_dtos = [c for c in client_dtos if str(c.id) == str(current_user.client_id)]
            
        # Convert DTOS to Responses
        return [
            ClientResponse(
                id = dto.id,
                name = dto.name,
                industry = dto.industry,
                contact_email = dto.contact_email,
                contact_phone = dto.contact_phone,
                address = dto.address
            )
            for dto in client_dtos
        ]

    async def update_client(self, client_id: UUID, client_data: ClientUpdate, current_user: User) -> ClientResponse:
        """
        Update a client.
        
        Args:
            client_id: UUID of client to update
            client_data: Updated client data
            current_user: Current authenticated user
            
        Returns:
            ClientResponse: Updated client
            
        Raises:
            HTTPException: If update fails or access denied
        """
        # Check access before attempting update
        self._check_client_access(client_id, current_user)
        
        try:
            # Convert Request to DTO
            update_dto = ClientDTO(
                id = client_id,
                name = client_data.name,
                industry = client_data.industry,
                contact_email = client_data.contact_email,
                contact_phone = client_data.contact_phone,
                address = client_data.address
            )

            # Send DTO to service
            result_dto = await self.client_service.update_client(update_dto, current_user)

            # Convert DTO to Response
            return ClientResponse(
                id = result_dto.id,
                name = result_dto.name,
                industry = result_dto.industry,
                contact_email = result_dto.contact_email,
                contact_phone = result_dto.contact_phone,
                address = result_dto.address
            )

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

    async def delete_client(self, client_id: UUID, current_user: User) -> None:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client to delete
            current_user: Current authenticated user
            
        Returns:
            None
            
        Raises:
            HTTPException: If deletion fails or access denied
        """
        # Check admin access for deletion
        self._check_admin_access(current_user)
        
        try:
            await self.client_service.delete_client(client_id, current_user)
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

    async def search_clients(self, search_term: str, current_user: User) -> List[ClientResponse]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            current_user: Current authenticated user
            
        Returns:
            List[ClientResponse]: List of matching clients
        """
        try:
            # Get Clients
            client_dtos = await self.client_service.search_clients(search_term)
        
            # Filter for client role
            if current_user.role.name == "client":
                client_dtos = [c for c in client_dtos if str(c.id) == str(current_user.client_id)]
            
            # Convert DTOS to Responses
            return [
                ClientResponse(
                    id = dto.id,
                    name = dto.name,
                    industry = dto.industry,
                    contact_email = dto.contact_email,
                    contact_phone = dto.contact_phone,
                    address = dto.address
                )
                for dto in client_dtos
            ]
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )