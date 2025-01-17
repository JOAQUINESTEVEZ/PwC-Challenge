from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, UTC
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.invoice_model import Invoice
from ..models.user_model import User
from ..repositories.invoice_repository import InvoiceRepository
from ..schemas.invoice_schema import InvoiceCreate, InvoiceUpdate
from ..models.audit_logs_model import AuditLog

class InvoiceService:
    """Service for handling invoice business logic."""
    
    def __init__(self, db: Session):
        self.invoice_repository = InvoiceRepository(Invoice, db)
        self.db = db

    def create_invoice(self, invoice_data: InvoiceCreate, current_user: User) -> Invoice:
        """Create a new invoice."""
        # Set the created_by field to current user
        invoice_dict = invoice_data.model_dump()
        invoice_dict["created_by"] = current_user.id
        
        # Set initial status if not provided
        if "status" not in invoice_dict or not invoice_dict["status"]:
            invoice_dict["status"] = "PENDING"
        
        invoice = self.invoice_repository.create(invoice_dict)
        
        # Create audit log
        audit_log = AuditLog(
            changed_by=current_user.id,
            table_name="invoices",
            record_id=invoice.id,
            change_type="create",
            change_details=f"Created invoice of {invoice.amount_due} for client {invoice.client_id}"
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return invoice

    def get_invoice(self, invoice_id: UUID, current_user: User) -> Invoice:
        """Get an invoice by ID."""
        invoice = self.invoice_repository.get(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Invoice not found",
                    "status": 404,
                    "detail": f"Invoice with id '{invoice_id}' not found",
                    "instance": f"/invoices/{invoice_id}"
                }
            )
            
        # If user is a client, they can only view their own invoices
        if current_user.role.name == "client" and invoice.client_id != current_user.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Access denied",
                    "status": 403,
                    "detail": "You can only view your own invoices",
                    "instance": f"/invoices/{invoice_id}"
                }
            )
            
        return invoice

    def search_invoices(self,
                     client_id: Optional[UUID] = None,
                     status: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None,
                     min_amount: Optional[float] = None,
                     max_amount: Optional[float] = None,
                     is_overdue: Optional[bool] = None,
                     current_user: User = None) -> List[Invoice]:
        """Search invoices with filters."""
        # If user is a client, force client_id filter to their own id
        if current_user.role.name == "client":
            client_id = current_user.client_id
            
        return self.invoice_repository.search_invoices(
            client_id=client_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            is_overdue=is_overdue
        )

    def update_invoice(self, 
                    invoice_id: UUID, 
                    invoice_data: InvoiceUpdate,
                    current_user: User) -> Invoice:
        """Update an existing invoice."""
        # Check if invoice exists
        invoice = self.get_invoice(invoice_id, current_user)
        
        # If updating amount paid, validate it doesn't exceed amount due
        if hasattr(invoice_data, 'amount_paid'):
            if invoice_data.amount_paid > invoice.amount_due:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "type": "about:blank",
                        "title": "Invalid amount",
                        "status": 400,
                        "detail": "Amount paid cannot exceed amount due",
                        "instance": f"/invoices/{invoice_id}"
                    }
                )
                
            # Update status if fully paid
            if invoice_data.amount_paid == invoice.amount_due:
                invoice_data.status = "PAID"
            elif invoice_data.amount_paid > 0:
                invoice_data.status = "PARTIALLY_PAID"
        
        updated_invoice = self.invoice_repository.update(invoice_id, invoice_data)
        
        # Create audit log
        audit_log = AuditLog(
            changed_by=current_user.id,
            table_name="invoices",
            record_id=invoice_id,
            change_type="update",
            change_details=f"Updated invoice {invoice_id}"
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return updated_invoice

    def delete_invoice(self, invoice_id: UUID, current_user: User) -> bool:
        """Delete an invoice."""
        # Check if invoice exists
        invoice = self.get_invoice(invoice_id, current_user)
        
        # Can't delete paid invoices
        if invoice.status == "PAID":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid operation",
                    "status": 400,
                    "detail": "Cannot delete paid invoices",
                    "instance": f"/invoices/{invoice_id}"
                }
            )
        
        result = self.invoice_repository.delete(invoice_id)
        
        if result:
            # Create audit log
            audit_log = AuditLog(
                changed_by=current_user.id,
                table_name="invoices",
                record_id=invoice_id,
                change_type="delete",
                change_details=f"Deleted invoice {invoice_id}"
            )
            self.db.add(audit_log)
            self.db.commit()
            
        return result

    def get_overdue_invoices(self, current_user: User) -> List[Invoice]:
        """Get all overdue invoices."""
        invoices = self.invoice_repository.get_overdue_invoices()
        
        # If user is a client, filter to only show their invoices
        if current_user.role.name == "client":
            invoices = [inv for inv in invoices if inv.client_id == current_user.client_id]
            
        return invoices