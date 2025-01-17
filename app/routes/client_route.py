from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..controllers.client_controller import ClientController
from ..schemas.client_schema import Client, ClientCreate, ClientUpdate
from ..dependencies.auth import get_current_user, check_permissions
from ..models.user_model import User

router = APIRouter()

@router.post("",
            response_model=Client,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(check_permissions("clients", "create"))],
            responses={
                401: {"description": "Not authenticated"},
                403: {"description": "Not enough permissions"},
                400: {"description": "Client already exists"}
            })
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Client:
    """
    Create a new client. Requires 'create' permission on 'clients' resource.
    """
    client_controller = ClientController(db)
    return await client_controller.create_client(client_data, current_user)

@router.get("/{client_id}",
           response_model=Client,
           dependencies=[Depends(check_permissions("clients", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Client not found"}
           })
async def get_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Client:
    """
    Get a specific client by ID. Requires 'read' permission on 'clients' resource.
    For client role, can only access own client information.
    """
    client_controller = ClientController(db)
    
    # If user has client role, they can only access their own client information
    if current_user.role.name == "client" and str(client_id) != getattr(current_user, "client_id", None):
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
        
    return await client_controller.get_client(client_id, current_user)

@router.get("",
           response_model=List[Client],
           dependencies=[Depends(check_permissions("clients", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"}
           })
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    search: Optional[str] = Query(None, description="Search term for client name or industry"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Client]:
    """
    Get all clients with pagination. Requires 'read' permission on 'clients' resource.
    For client role, only returns their own client information.
    """
    client_controller = ClientController(db)
    
    if search:
        clients = await client_controller.search_clients(search)
    else:
        clients = await client_controller.get_all_clients(skip, limit)
    
    # If user has client role, filter to only show their own client
    if current_user.role.name == "client":
        clients = [c for c in clients if str(c.id) == getattr(current_user, "client_id", None)]
    
    return clients

@router.put("/{client_id}",
           response_model=Client,
           dependencies=[Depends(check_permissions("clients", "update"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Client not found"},
               400: {"description": "Client name already exists"}
           })
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Client:
    """
    Update a client. Requires 'update' permission on 'clients' resource.
    """
    client_controller = ClientController(db)
    return await client_controller.update_client(client_id, client_data, current_user)

@router.delete("/{client_id}",
             status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(check_permissions("clients", "delete"))],
             responses={
                 401: {"description": "Not authenticated"},
                 403: {"description": "Not enough permissions"},
                 404: {"description": "Client not found"}
             })
async def delete_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a client. Requires 'delete' permission on 'clients' resource.
    Only admin role can delete clients.
    """
    # Additional check for admin role
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "type": "about:blank",
                "title": "Forbidden",
                "status": 403,
                "detail": "Only administrators can delete clients",
                "instance": f"/clients/{client_id}"
            }
        )
    
    client_controller = ClientController(db)
    result = await client_controller.delete_client(client_id, current_user)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "about:blank",
                "title": "Not Found",
                "status": 404,
                "detail": f"Client with id '{client_id}' not found",
                "instance": f"/clients/{client_id}"
            }
        )