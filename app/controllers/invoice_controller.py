from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from ..services.invoice_service import InvoiceService
from ..models.user_model import User
from ..schemas.invoice_schema import (
    Invoice,
    InvoiceCreate,
    InvoiceUpdate
)

class InvoiceController:
    """Controller for managing invoice operations."""
    
    def __init__(self, db: Session):
        self.invoice_service = InvoiceService(db)

    async def create_invoice(self, 
                         invoice_data: InvoiceCreate,
                         current_user: User) -> Invoice:
        """Create a new invoice."""
        return self.invoice_service.create_invoice(invoice_data, current_user)

    async def get_invoice(self, 
                       invoice_id: UUID, 
                       current_user: User) -> Invoice:
        """Get a specific invoice by ID."""
        return self.invoice_service.get_invoice(invoice_id, current_user)

    async def search_invoices(self,
                          client_id: Optional[UUID] = None,
                          status: Optional[str] = None,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None,
                          min_amount: Optional[float] = None,
                          max_amount: Optional[float] = None,
                          is_overdue: Optional[bool] = None,
                          current_user: User = None) -> List[Invoice]:
        """Search invoices with various filters."""
        return self.invoice_service.search_invoices(
            client_id=client_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            is_overdue=is_overdue,
            current_user=current_user
        )

    async def update_invoice(self,
                         invoice_id: UUID,
                         invoice_data: InvoiceUpdate,
                         current_user: User) -> Invoice:
        """Update an existing invoice."""
        return self.invoice_service.update_invoice(
            invoice_id,
            invoice_data,
            current_user
        )

    async def delete_invoice(self,
                         invoice_id: UUID,
                         current_user: User) -> bool:
        """Delete an invoice."""
        return self.invoice_service.delete_invoice(invoice_id, current_user)

    async def get_overdue_invoices(self, current_user: User) -> List[Invoice]:
        """Get all overdue invoices."""
        return self.invoice_service.get_overdue_invoices(current_user)