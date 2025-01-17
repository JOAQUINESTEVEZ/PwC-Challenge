from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..services.invoice_service import InvoiceService
from ..models.user_model import User
from ..schemas.invoice_schema import (
    Invoice,
    InvoiceCreate,
    InvoiceUpdate
)

class InvoiceController:
    """
    Controller for managing invoice operations.
    Handles access control and coordinates between routes and services.
    """
    
    def __init__(self, db: Session):
        """Initialize controller with database session."""
        self.invoice_service = InvoiceService(db)

    def _check_invoice_access(self, invoice: Invoice, current_user: User):
        """
        Check if user has access to invoice.
        
        Args:
            invoice: Invoice to check
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If access is denied
        """
        if current_user.role.name == "client" and invoice.client_id != current_user.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Access denied",
                    "status": 403,
                    "detail": "You can only access your own invoices",
                    "instance": f"/invoices/{invoice.id}"
                }
            )

    async def create_invoice(self, invoice_data: InvoiceCreate, current_user: User) -> Invoice:
        """
        Create a new invoice.
        
        Args:
            invoice_data: Data for invoice creation
            current_user: Current authenticated user
            
        Returns:
            Invoice: Created invoice
            
        Raises:
            HTTPException: If creation fails or permissions not met
        """
        try:
            # For client role, ensure they can only create invoices for themselves
            if current_user.role.name == "client":
                if str(invoice_data.client_id) != str(current_user.client_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "type": "about:blank",
                            "title": "Access denied",
                            "status": 403,
                            "detail": "You can only create invoices for your own account",
                            "instance": "/invoices"
                        }
                    )
            
            return self.invoice_service.create_invoice(invoice_data, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid invoice data",
                    "status": 400,
                    "detail": str(e),
                    "instance": "/invoices"
                }
            )

    async def get_invoice(self, invoice_id: UUID, current_user: User) -> Invoice:
        """
        Get a specific invoice by ID.
        
        Args:
            invoice_id: UUID of invoice to retrieve
            current_user: Current authenticated user
            
        Returns:
            Invoice: Retrieved invoice
            
        Raises:
            HTTPException: If invoice not found or access denied
        """
        try:
            invoice = self.invoice_service.get_invoice(invoice_id)
            self._check_invoice_access(invoice, current_user)
            return invoice
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Invoice not found",
                    "status": 404,
                    "detail": str(e),
                    "instance": f"/invoices/{invoice_id}"
                }
            )

    async def search_invoices(self,
                          client_id: Optional[UUID] = None,
                          status: Optional[str] = None,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None,
                          min_amount: Optional[float] = None,
                          max_amount: Optional[float] = None,
                          is_overdue: Optional[bool] = None,
                          current_user: User = None) -> List[Invoice]:
        """
        Search invoices with filters.
        
        Args:
            client_id: Optional client filter
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            min_amount: Optional minimum amount filter
            max_amount: Optional maximum amount filter
            is_overdue: Optional overdue status filter
            current_user: Current authenticated user
            
        Returns:
            List[Invoice]: List of matching invoices
            
        Raises:
            HTTPException: If search parameters are invalid
        """
        try:
            # For client role, force client_id filter to their own id
            if current_user.role.name == "client":
                client_id = current_user.client_id

            return self.invoice_service.search_invoices(
                client_id=client_id,
                status=status,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount,
                is_overdue=is_overdue
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid search parameters",
                    "status": 400,
                    "detail": str(e),
                    "instance": "/invoices"
                }
            )

    async def update_invoice(self,
                         invoice_id: UUID,
                         invoice_data: InvoiceUpdate,
                         current_user: User) -> Invoice:
        """
        Update an existing invoice.
        
        Args:
            invoice_id: UUID of invoice to update
            invoice_data: Updated invoice data
            current_user: Current authenticated user
            
        Returns:
            Invoice: Updated invoice
            
        Raises:
            HTTPException: If update fails or access denied
        """
        try:
            # First get the invoice to check access
            invoice = self.invoice_service.get_invoice(invoice_id)
            self._check_invoice_access(invoice, current_user)
            
            return self.invoice_service.update_invoice(invoice_id, invoice_data, current_user)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "type": "about:blank",
                        "title": "Invoice not found",
                        "status": 404,
                        "detail": str(e),
                        "instance": f"/invoices/{invoice_id}"
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid update data",
                    "status": 400,
                    "detail": str(e),
                    "instance": f"/invoices/{invoice_id}"
                }
            )

    async def delete_invoice(self, invoice_id: UUID, current_user: User) -> bool:
        """
        Delete an invoice.
        
        Args:
            invoice_id: UUID of invoice to delete
            current_user: Current authenticated user
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            HTTPException: If deletion fails or access denied
        """
        try:
            # First get the invoice to check access
            invoice = self.invoice_service.get_invoice(invoice_id)
            self._check_invoice_access(invoice, current_user)
            
            return self.invoice_service.delete_invoice(invoice_id, current_user)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "type": "about:blank",
                        "title": "Invoice not found",
                        "status": 404,
                        "detail": str(e),
                        "instance": f"/invoices/{invoice_id}"
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Delete operation failed",
                    "status": 400,
                    "detail": str(e),
                    "instance": f"/invoices/{invoice_id}"
                }
            )

    async def get_overdue_invoices(self, current_user: User) -> List[Invoice]:
        """
        Get all overdue invoices.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            List[Invoice]: List of overdue invoices
        """
        return self.invoice_service.get_overdue_invoices(current_user)