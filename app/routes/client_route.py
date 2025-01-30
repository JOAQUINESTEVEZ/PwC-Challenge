from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import StreamingResponse
from dependency_injector.wiring import inject, Provide

from ..interfaces.controllers.client_controller import IClientController
from ..interfaces.controllers.report_controller import IReportController
from ..schemas.request.client import ClientCreate, ClientUpdate
from ..schemas.response.client import ClientResponse
from ..dependencies.auth import get_current_user, check_permissions
from ..dependencies.rate_limit import check_user_pdf_rate_limit
from ..entities.user import User
from ..container import Container

router = APIRouter()

@router.post("",
            response_model=ClientResponse,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(check_permissions("clients", "create"))],
            responses={
                401: {"description": "Not authenticated"},
                403: {"description": "Not enough permissions"},
                400: {"description": "Client already exists"}
            })
@inject
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    client_controller: IClientController = Depends(Provide[Container.client_controller])
) -> ClientResponse:
    """
    Create a new client. Requires 'create' permission on 'clients' resource.
    
    Args:
        client_data: ClientRequest data for creation
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ClientResponse: Created client
        
    Raises:
        HTTPException: If client creation fails or permission denied
    """
    return await client_controller.create_client(client_data, current_user)

@router.get("/{client_id}",
           response_model=ClientResponse,
           dependencies=[Depends(check_permissions("clients", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Client not found"}
           })
@inject
async def get_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    client_controller: IClientController = Depends(Provide[Container.client_controller])
) -> ClientResponse:
    """
    Get a specific client by ID. Requires 'read' permission on 'clients' resource.
    
    Args:
        client_id: UUID of client to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ClientResponse: Retrieved client
        
    Raises:
        HTTPException: If client not found or access denied
    """
    return await client_controller.get_client(client_id, current_user)

@router.get("",
           response_model=List[ClientResponse],
           dependencies=[Depends(check_permissions("clients", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"}
           })
@inject
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    search: Optional[str] = Query(None, description="Search term for client name or industry"),
    current_user: User = Depends(get_current_user),
    client_controller: IClientController = Depends(Provide[Container.client_controller])
) -> List[ClientResponse]:
    """
    Get all clients with pagination. Requires 'read' permission on 'clients' resource.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term for filtering
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[ClientResponse]: List of clients matching criteria
    """
    if search:
        return await client_controller.search_clients(search, current_user)
    return await client_controller.get_all_clients(skip, limit, current_user)

@router.put("/{client_id}",
           response_model=ClientResponse,
           dependencies=[Depends(check_permissions("clients", "update"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Client not found"},
               400: {"description": "Client name already exists"}
           })
@inject
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_user),
    client_controller: IClientController = Depends(Provide[Container.client_controller])
) -> ClientResponse:
    """
    Update a client. Requires 'update' permission on 'clients' resource.
    
    Args:
        client_id: UUID of client to update
        client_data: Updated client data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ClientResponse: Updated client
        
    Raises:
        HTTPException: If client not found or update fails
    """
    return await client_controller.update_client(client_id, client_data, current_user)

@router.delete("/{client_id}",
             status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(check_permissions("clients", "delete"))],
             responses={
                 401: {"description": "Not authenticated"},
                 403: {"description": "Not enough permissions"},
                 404: {"description": "Client not found"}
             })
@inject
async def delete_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    client_controller: IClientController = Depends(Provide[Container.client_controller])
):
    """
    Delete a client. Requires 'delete' permission on 'clients' resource.
    
    Args:
        client_id: UUID of client to delete
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If client not found or deletion fails
    """
    await client_controller.delete_client(client_id, current_user)
    
    # If client was deleted successfully, return 204 No Content
    # If deletion failed, controller would have raised appropriate HTTPException
    return None

@router.get("/{client_id}/report",
           dependencies=[
               Depends(check_permissions("clients", "read")),
               Depends(check_user_pdf_rate_limit)
            ],
           responses={
                401: {"description": "Not authenticated"},
                403: {"description": "Not enough permissions"},
                404: {"description": "Client not found"},
                400: {
                   "description": "Bad Request",
                   "content": {
                       "application/json": {
                           "example": {
                               "type": "about:blank",
                               "title": "Bad Request",
                               "status": 400,
                               "detail": "At least one section (transactions or invoices) must be included",
                               "instance": "/clients/{client_id}/report"
                           }
                       }
                   }
               },
               429: {
                   "description": "Too Many Requests",
                   "content": {
                       "application/json": {
                           "example": {
                               "type": "about:blank",
                               "title": "Too Many Requests",
                               "status": 429,
                               "detail": "Rate limit exceeded. Please try again in X seconds.",
                               "instance": "/clients/{client_id}/report"
                           }
                       }
                   }
               }
           },
           response_class=StreamingResponse)
@inject
async def get_client_report(
    client_id: UUID,
    include_transactions: bool = Query(True, description="Include transactions section in report"),
    include_invoices: bool = Query(True, description="Include invoices section in report"),
    current_user: User = Depends(get_current_user),
    report_controller: IReportController = Depends(Provide[Container.report_controller])
):
    """
    Get a PDF report of client's financial history. Requires 'read' permission.
    
    Args:
        client_id: UUID of client
        include_transactions: Whether to include transactions section
        include_invoices: Whether to include invoices section
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        StreamingResponse: PDF report as streaming response
        
    Raises:
        HTTPException: If client not found or access denied
    """
    if not include_transactions and not include_invoices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "about:blank",
                "title": "Bad Request",
                "status": 400,
                "detail": "At least one section (transactions or invoices) must be included",
                "instance": f"/clients/{client_id}/report"
            }
        )
    pdf_buffer = await report_controller.generate_client_financial_report(
        client_id,
        current_user,
        include_transactions=include_transactions,
        include_invoices=include_invoices
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="client_financial_report.pdf"'
        }
    )