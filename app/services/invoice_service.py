from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, UTC
from decimal import Decimal
from sqlalchemy.orm import Session
from ..models.invoice_model import Invoice
from ..models.user_model import User
from ..repositories.invoice_repository import InvoiceRepository
from ..schemas.invoice_schema import InvoiceCreate, InvoiceUpdate
from ..models.audit_logs_model import AuditLog

class InvoiceService:
    """
    Service for handling invoice business logic.
    Manages invoice operations and business rules.
    """
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.invoice_repository = InvoiceRepository(Invoice, db)
        self.db = db

    def _create_audit_log(self, user_id: UUID, record_id: UUID, change_type: str, details: str) -> None:
        """
        Create an audit log entry for invoice changes.
        
        Args:
            user_id: ID of user making the change
            record_id: ID of affected invoice
            change_type: Type of change (create, update, delete)
            details: Change details
        """
        audit_log = AuditLog(
            changed_by=user_id,
            table_name="invoices",
            record_id=record_id,
            change_type=change_type,
            change_details=details,
            timestamp=datetime.now(UTC)
        )
        self.db.add(audit_log)
        self.db.commit()

    def _validate_invoice_amounts(self, amount_due: Decimal, amount_paid: Optional[Decimal] = None) -> None:
        """
        Validate invoice amounts.
        
        Args:
            amount_due: Total amount due
            amount_paid: Amount paid (if provided)
            
        Raises:
            ValueError: If amounts are invalid
        """
        if amount_due <= Decimal('0'):
            raise ValueError("Invoice amount must be positive")
            
        if amount_paid is not None:
            if amount_paid < Decimal('0'):
                raise ValueError("Paid amount cannot be negative")
            if amount_paid > amount_due:
                raise ValueError("Paid amount cannot exceed amount due")

    def _validate_dates(self, invoice_date: date, due_date: date) -> None:
        """
        Validate invoice dates.
        
        Args:
            invoice_date: Date of invoice creation
            due_date: Payment due date
            
        Raises:
            ValueError: If dates are invalid
        """
        if due_date < invoice_date:
            raise ValueError("Due date cannot be before invoice date")

    def _determine_status(self, amount_due: Decimal, amount_paid: Decimal) -> str:
        """
        Determine invoice status based on amounts.
        
        Args:
            amount_due: Total amount due
            amount_paid: Amount already paid
            
        Returns:
            str: Invoice status (PAID, PARTIALLY_PAID, or PENDING)
        """
        if amount_paid >= amount_due:
            return "PAID"
        elif amount_paid > 0:
            return "PARTIALLY_PAID"
        return "PENDING"

    def create_invoice(self, invoice_data: InvoiceCreate, current_user: User) -> Invoice:
        """
        Create a new invoice.
        
        Args:
            invoice_data: Data for invoice creation
            current_user: User creating the invoice
            
        Returns:
            Invoice: Created invoice
            
        Raises:
            ValueError: If validation fails
        """
        # Validate amounts
        self._validate_invoice_amounts(invoice_data.amount_due, invoice_data.amount_paid)
        
        # Validate dates
        self._validate_dates(invoice_data.invoice_date, invoice_data.due_date)
        
        # Set status based on paid amount
        invoice_dict = invoice_data.model_dump()
        invoice_dict["created_by"] = current_user.id
        invoice_dict["status"] = self._determine_status(
            invoice_dict["amount_due"], 
            invoice_dict.get("amount_paid", Decimal('0'))
        )
        
        # Create invoice
        invoice = self.invoice_repository.create(invoice_dict)
        
        # Create audit log
        self._create_audit_log(
            user_id=current_user.id,
            record_id=invoice.id,
            change_type="create",
            details=f"Created invoice of {invoice.amount_due} for client {invoice.client_id}"
        )
        
        return invoice

    def get_invoice(self, invoice_id: UUID) -> Invoice:
        """
        Get invoice by ID.
        
        Args:
            invoice_id: UUID of invoice to retrieve
            
        Returns:
            Invoice: Found invoice
            
        Raises:
            ValueError: If invoice not found
        """
        invoice = self.invoice_repository.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with id '{invoice_id}' not found")
            
        return invoice

    def search_invoices(self,
                     client_id: Optional[UUID] = None,
                     status: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None,
                     min_amount: Optional[float] = None,
                     max_amount: Optional[float] = None,
                     is_overdue: Optional[bool] = None) -> List[Invoice]:
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
            List[Invoice]: List of matching invoices
            
        Raises:
            ValueError: If search parameters are invalid
        """
        # Validate date range
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date cannot be before start date")
            
        return self.invoice_repository.search_invoices(
            client_id=client_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            is_overdue=is_overdue
        )

    def update_invoice(self, invoice_id: UUID, invoice_data: InvoiceUpdate, current_user: User) -> Invoice:
        """
        Update an existing invoice.
        
        Args:
            invoice_id: UUID of invoice to update
            invoice_data: Updated invoice data
            current_user: User performing the update
            
        Returns:
            Invoice: Updated invoice
            
        Raises:
            ValueError: If invoice not found or validation fails
        """
        # Get current invoice state
        invoice = self.get_invoice(invoice_id)
        
        # Cannot update paid invoices
        if invoice.status == "PAID" and any([
            invoice_data.amount_due is not None,
            invoice_data.invoice_date is not None,
            invoice_data.due_date is not None
        ]):
            raise ValueError("Cannot modify core fields of a paid invoice")
        
        # Validate amounts if updating
        if invoice_data.amount_due is not None or invoice_data.amount_paid is not None:
            amount_due = invoice_data.amount_due or invoice.amount_due
            amount_paid = invoice_data.amount_paid or invoice.amount_paid
            self._validate_invoice_amounts(amount_due, amount_paid)
            
            # Update status based on new amounts
            invoice_data.status = self._determine_status(amount_due, amount_paid)
        
        # Validate dates if updating
        if invoice_data.invoice_date or invoice_data.due_date:
            self._validate_dates(
                invoice_data.invoice_date or invoice.invoice_date,
                invoice_data.due_date or invoice.due_date
            )
        
        # Perform update
        updated_invoice = self.invoice_repository.update(invoice_id, invoice_data)
        
        # Create audit log
        self._create_audit_log(
            user_id=current_user.id,
            record_id=invoice_id,
            change_type="update",
            details=f"Updated invoice {invoice_id}"
        )
        
        return updated_invoice

    def delete_invoice(self, invoice_id: UUID, current_user: User) -> bool:
        """
        Delete an invoice.
        
        Args:
            invoice_id: UUID of invoice to delete
            current_user: User performing the deletion
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            ValueError: If invoice not found or cannot be deleted
        """
        # Get current invoice state
        invoice = self.get_invoice(invoice_id)
        
        # Cannot delete paid invoices
        if invoice.status == "PAID":
            raise ValueError("Cannot delete paid invoices")
        
        result = self.invoice_repository.delete(invoice_id)
        
        if result:
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                record_id=invoice_id,
                change_type="delete",
                details=f"Deleted invoice {invoice_id}"
            )
        
        return result

    def get_overdue_invoices(self, current_user: User) -> List[Invoice]:
        """
        Get all overdue invoices.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            List[Invoice]: List of overdue invoices
        """
        return self.invoice_repository.get_overdue_invoices()