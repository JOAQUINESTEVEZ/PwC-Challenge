from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, UTC
from decimal import Decimal
from sqlalchemy.orm import Session
from ..repositories.invoice_repository import InvoiceRepository
from ..entities.user import User
from ..entities.invoice import Invoice, InvoiceStatus
from ..schemas.dto.invoice_dto import InvoiceDTO

class InvoiceService:
    """
    Service for handling invoice business logic.
    Manages invoice operations and business rules.
    """
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.invoice_repository = InvoiceRepository(db)

    # def _create_audit_log(self, user_id: UUID, record_id: UUID, change_type: str, details: str) -> None:
    #     """
    #     Create an audit log entry for invoice changes.
        
    #     Args:
    #         user_id: ID of user making the change
    #         record_id: ID of affected invoice
    #         change_type: Type of change (create, update, delete)
    #         details: Change details
    #     """
    #     audit_log = AuditLog(
    #         changed_by=user_id,
    #         table_name="invoices",
    #         record_id=record_id,
    #         change_type=change_type,
    #         change_details=details,
    #         timestamp=datetime.now(UTC)
    #     )
    #     self.db.add(audit_log)
    #     self.db.commit()

    async def create_invoice(self, invoice_dto: InvoiceDTO) -> InvoiceDTO:
        """
        Create a new invoice.
        
        Args:
            invoice_dto: Data for invoice creation
            
        Returns:
            InvoiceDetailDTO: Created invoice
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Convert DTO to entity
            invoice = Invoice(
                id=None,
                client_id=invoice_dto.client_id,
                created_by=invoice_dto.created_by,
                invoice_date=invoice_dto.invoice_date,
                due_date=invoice_dto.due_date,
                amount_due=invoice_dto.amount_due,
                amount_paid=invoice_dto.amount_paid,
                status=InvoiceStatus.PENDING,  # Set initial status
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

            # Apply business rules
            invoice.validate_amounts()
            invoice.validate_dates()
            invoice.update_status()

            # Save through repository
            saved_invoice = await self.invoice_repository.create(invoice)

            # Convert entity to DTO and return
            return InvoiceDTO.from_entity(saved_invoice)
        
        except Exception as e:
            raise ValueError(f"Error creating invoice: {str(e)}")
        
        # # Create audit log
        # self._create_audit_log(
        #     user_id=current_user.id,
        #     record_id=invoice.id,
        #     change_type="create",
        #     details=f"Created invoice of {invoice.amount_due} for client {invoice.client_id}"
        # )
        
        # return invoice

    async def get_invoice(self, invoice_id: UUID) -> InvoiceDTO:
        """
        Get invoice by ID.
        
        Args:
            invoice_id: UUID of invoice to retrieve
            
        Returns:
            InvoiceDetailDTO: Found invoice
            
        Raises:
            ValueError: If invoice not found
        """
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with id {invoice_id} not found")

        return InvoiceDTO.from_entity(invoice)

    async def search_invoices(self,
                     client_id: Optional[UUID] = None,
                     status: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None,
                     min_amount: Optional[float] = None,
                     max_amount: Optional[float] = None,
                     is_overdue: Optional[bool] = None) -> List[InvoiceDTO]:
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
            
        Returns:
            List[InvoiceListDTO]: List of matching invoices
            
        Raises:
            ValueError: If search parameters are invalid
        """
        try:
            # Validate date range if provided
            if start_date and end_date and end_date < start_date:
                raise ValueError("End date cannot be before start date")

            # Convert amounts to Decimal if provided
            min_amount_decimal = Decimal(str(min_amount)) if min_amount is not None else None
            max_amount_decimal = Decimal(str(max_amount)) if max_amount is not None else None

            # Get filtered invoices
            invoices = await self.invoice_repository.search(
                client_id=client_id,
                status=status,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount_decimal,
                max_amount=max_amount_decimal,
                is_overdue=is_overdue
            )

            # Convert to DTOs
            return [
                InvoiceDTO.from_entity(invoice)
                for invoice in invoices
            ]

        except Exception as e:
            raise ValueError(f"Error searching invoices: {str(e)}")

    async def update_invoice(self, invoice_dto: InvoiceDTO, current_user: User) -> InvoiceDTO:
        """
        Update an existing invoice.
        
        Args:
            invoice_id: UUID of invoice to update
            invoice_dto: Updated invoice dto
            current_user: User performing the update
            
        Returns:
            InvoiceDetailDTO: Updated invoice
            
        Raises:
            ValueError: If invoice not found or validation fails
        """
        try:
            # Get existing invoice
            existing_invoice = await self.invoice_repository.get_by_id(invoice_dto.id)
            if not existing_invoice:
                raise ValueError(f"Invoice with id {invoice_dto.id} not found")

            # Update fields while preserving others
            if invoice_dto.invoice_date:
                existing_invoice.invoice_date = invoice_dto.invoice_date
            if invoice_dto.due_date:
                existing_invoice.due_date = invoice_dto.due_date
            if invoice_dto.amount_due is not None:
                existing_invoice.amount_due = invoice_dto.amount_due
            if invoice_dto.amount_paid is not None:
                existing_invoice.amount_paid = invoice_dto.amount_paid

            # Apply business rules
            existing_invoice.validate_amounts()
            existing_invoice.validate_dates()
            existing_invoice.update_status()
            existing_invoice.updated_at = datetime.now(UTC)

            # Save updates
            updated_invoice = await self.invoice_repository.update(existing_invoice)

            # Convert entity to DTO and return
            return InvoiceDTO.from_entity(updated_invoice)

        except Exception as e:
            raise ValueError(f"Error updating invoice: {str(e)}")
        
        # # Create audit log
        # self._create_audit_log(
        #     user_id=current_user.id,
        #     record_id=invoice_id,
        #     change_type="update",
        #     details=f"Updated invoice {invoice_id}"
        # )

    async def delete_invoice(self, invoice_id: UUID, current_user: User) -> None:
        """
        Delete an invoice.
        
        Args:
            invoice_id: UUID of invoice to delete
            current_user: User performing the deletion
            
        Returns:
            None
            
        Raises:
            ValueError: If invoice not found or cannot be deleted
        """
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with id {invoice_id} not found")

        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("Cannot delete a paid invoice")

        await self.invoice_repository.delete(invoice_id)

    async def get_overdue_invoices(self, client_id: Optional[UUID] = None) -> List[InvoiceDTO]:
        """
        Get all overdue invoices.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            List[InvoiceListDTO]: List of overdue invoices
        """
        try:
            # Get overdue invoices
            invoices = await self.invoice_repository.get_overdue(client_id)

            # Convert to DTOs
            return [
                InvoiceDTO.from_entity(invoice)
                for invoice in invoices
            ]

        except Exception as e:
            raise ValueError(f"Error getting overdue invoices: {str(e)}")