from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..controllers.invoice_controller import InvoiceController
from ..schemas.invoice_schema import (
    Invoice,
    InvoiceCreate,
    InvoiceUpdate
)
from ..dependencies.auth import get_current_user, check_permissions
from ..models.user_model import User

router = APIRouter()

@router.post("",
            response_model=Invoice,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(check_permissions("invoices", "create"))],
            responses={
                401: {"description": "Not authenticated"},
                403: {"description": "Not enough permissions"},
                404: {"description": "Client not found"},
                400: {"description": "Invalid invoice data"}
            })
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Invoice:
    """
    Create a new invoice.
    
    Args:
        invoice_data: Data for the new invoice
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Invoice: Created invoice
        
    Raises:
        HTTPException: If creation fails or permissions not met
    """
    controller = InvoiceController(db)
    return await controller.create_invoice(invoice_data, current_user)

@router.get("/overdue",
           response_model=List[Invoice],
           dependencies=[Depends(check_permissions("invoices", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"}
           })
async def get_overdue_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Invoice]:
    """
    Get all overdue invoices.
    Clients can only view their own overdue invoices.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[Invoice]: List of overdue invoices
    """
    controller = InvoiceController(db)
    return await controller.get_overdue_invoices(current_user)

@router.get("/{invoice_id}",
           response_model=Invoice,
           dependencies=[Depends(check_permissions("invoices", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Invoice not found"}
           })
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Invoice:
    """
    Get a specific invoice by ID.
    Clients can only view their own invoices.
    
    Args:
        invoice_id: UUID of invoice to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Invoice: Retrieved invoice
        
    Raises:
        HTTPException: If invoice not found or access denied
    """
    controller = InvoiceController(db)
    return await controller.get_invoice(invoice_id, current_user)

@router.get("",
           response_model=List[Invoice],
           dependencies=[Depends(check_permissions("invoices", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"}
           })
async def search_invoices(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    min_amount: Optional[float] = Query(None, description="Minimum invoice amount"),
    max_amount: Optional[float] = Query(None, description="Maximum invoice amount"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue invoices"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Invoice]:
    """
    Search and filter invoices.
    Clients can only view their own invoices.
    
    Args:
        client_id: Optional client filter
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        min_amount: Optional minimum amount filter
        max_amount: Optional maximum amount filter
        is_overdue: Optional overdue status filter
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[Invoice]: List of matching invoices
    """
    controller = InvoiceController(db)
    return await controller.search_invoices(
        client_id=client_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        is_overdue=is_overdue,
        current_user=current_user
    )

@router.put("/{invoice_id}",
           response_model=Invoice,
           dependencies=[Depends(check_permissions("invoices", "update"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Invoice not found"},
               400: {"description": "Invalid update data"}
           })
async def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Invoice:
    """
    Update an existing invoice.
    Cannot increase amount_paid beyond amount_due.
    
    Args:
        invoice_id: UUID of invoice to update
        invoice_data: Updated invoice data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Invoice: Updated invoice
        
    Raises:
        HTTPException: If invoice not found or update fails
    """
    controller = InvoiceController(db)
    return await controller.update_invoice(invoice_id, invoice_data, current_user)

@router.delete("/{invoice_id}",
             status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(check_permissions("invoices", "delete"))],
             responses={
                 401: {"description": "Not authenticated"},
                 403: {"description": "Not enough permissions"},
                 404: {"description": "Invoice not found"},
                 400: {"description": "Cannot delete paid invoice"}
             })
async def delete_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an invoice.
    Cannot delete paid invoices.
    
    Args:
        invoice_id: UUID of invoice to delete
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If invoice not found or deletion fails
    """
    controller = InvoiceController(db)
    await controller.delete_invoice(invoice_id, current_user)
    return None