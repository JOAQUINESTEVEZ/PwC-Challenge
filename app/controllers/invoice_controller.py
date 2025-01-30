from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException, status

from ..interfaces.controllers.invoice_controller import IInvoiceController
from ..interfaces.services.invoice_service import IInvoiceService
from ..entities.user import User
from ..schemas.request.invoice import InvoiceCreate, InvoiceUpdate
from ..schemas.response.invoice import InvoiceResponse
from ..schemas.dto.invoice_dto import InvoiceDTO

class InvoiceController(IInvoiceController):
    """
    Controller for managing invoice operations.
    Handles access control and coordinates between routes and services.
    """
    
    def __init__(self, invoice_service: IInvoiceService):
        """Initialize controller with database session."""
        self.invoice_service = invoice_service

    def _check_invoice_access(self, invoice_dto: InvoiceDTO, current_user: User):
        """
        Check if user has access to invoice.
        
        Args:
            invoice: Invoice to check
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If access is denied
        """
        if current_user.role.name == "client" and invoice_dto.client_id != current_user.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Access denied",
                    "status": 403,
                    "detail": "You can only access your own invoices",
                    "instance": f"/invoices/{invoice_dto.id}"
                }
            )

    async def create_invoice(self, invoice_data: InvoiceCreate, current_user: User) -> InvoiceResponse:
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
            # Convert Request to DTO
            invoice_dto = InvoiceDTO(
                id=None,
                client_id=invoice_data.client_id,
                invoice_date=invoice_data.invoice_date,
                due_date=invoice_data.due_date,
                amount_due=invoice_data.amount_due,
                amount_paid=invoice_data.amount_paid or 0,
                created_by=current_user.id,
                status=None
            )
            
            # Send DTO to service, get DTO back
            result_dto = await self.invoice_service.create_invoice(invoice_dto, current_user)

            # Convert DTO to Response
            return InvoiceResponse(
                id=result_dto.id,
                client_id=result_dto.client_id,
                invoice_date=result_dto.invoice_date,
                due_date=result_dto.due_date,
                amount_due=result_dto.amount_due,
                amount_paid=result_dto.amount_paid,
                status=result_dto.status,
                created_by=result_dto.created_by
            )
            
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

    async def get_invoice(self, invoice_id: UUID, current_user: User) -> InvoiceResponse:
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
            result_dto = await self.invoice_service.get_invoice(invoice_id)
            
            # Access control
            self._check_invoice_access(result_dto, current_user)
                
             # Convert DTO to Response
            return InvoiceResponse(
                id=result_dto.id,
                client_id=result_dto.client_id,
                invoice_date=result_dto.invoice_date,
                due_date=result_dto.due_date,
                amount_due=result_dto.amount_due,
                amount_paid=result_dto.amount_paid,
                status=result_dto.status,
                created_by=result_dto.created_by
            )
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
                          current_user: User = None) -> List[InvoiceResponse]:
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

            result_dtos = await self.invoice_service.search_invoices(
                client_id=client_id,
                status=status,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount,
                is_overdue=is_overdue
            )
            # Convert DTOs to Responses
            return [
                InvoiceResponse(
                    id=dto.id,
                    client_id=dto.client_id,
                    invoice_date=dto.invoice_date,
                    due_date=dto.due_date,
                    amount_due=dto.amount_due,
                    amount_paid=dto.amount_paid,
                    status=dto.status,
                    created_by=dto.created_by
                )
                for dto in result_dtos
            ]

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
                         current_user: User) -> InvoiceResponse:
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
            # Convert Request to DTO
            update_dto = InvoiceDTO(
                id=invoice_id,
                client_id=None,  # Can't update client_id
                invoice_date=invoice_data.invoice_date,
                due_date=invoice_data.due_date,
                amount_due=invoice_data.amount_due,
                amount_paid=invoice_data.amount_paid,
                status=None,  # Will be calculated by service
                created_by=None  # Can't update created_by
            )

            # Send DTO to service, get DTO back
            result_dto = await self.invoice_service.update_invoice(update_dto, current_user)

            # Convert DTO to Response
            return InvoiceResponse(
                id=result_dto.id,
                client_id=result_dto.client_id,
                invoice_date=result_dto.invoice_date,
                due_date=result_dto.due_date,
                amount_due=result_dto.amount_due,
                amount_paid=result_dto.amount_paid,
                status=result_dto.status,
                created_by=result_dto.created_by
            )
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

    async def delete_invoice(self, invoice_id: UUID, current_user: User) -> None:
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
            # Simply pass ID to service
            await self.invoice_service.delete_invoice(invoice_id, current_user)
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

    async def get_overdue_invoices(self, current_user: User) -> List[InvoiceResponse]:
        """
        Get all overdue invoices.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            List[Invoice]: List of overdue invoices
        """
        try:
            # Pass client_id if it's a client user
            client_id = current_user.client_id if current_user.role.name == "client" else None
            
            # Get DTOs from service
            result_dtos = await self.invoice_service.get_overdue_invoices(client_id)

            # Convert DTOs to Responses
            return [
                InvoiceResponse(
                    id=dto.id,
                    client_id=dto.client_id,
                    invoice_date=dto.invoice_date,
                    due_date=dto.due_date,
                    amount_due=dto.amount_due,
                    amount_paid=dto.amount_paid,
                    status=dto.status,
                    created_by=dto.created_by
                )
                for dto in result_dtos
            ]

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))