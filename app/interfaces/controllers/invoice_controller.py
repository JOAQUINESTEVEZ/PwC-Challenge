# interfaces/controller/invoice_controller.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from ...entities.user import User
from ...schemas.request.invoice import InvoiceCreate, InvoiceUpdate
from ...schemas.response.invoice import InvoiceResponse

class IInvoiceController(ABC):
    @abstractmethod
    async def create_invoice(
        self,
        invoice_data: InvoiceCreate,
        current_user: User
    ) -> InvoiceResponse:
        """Create a new invoice."""
        pass

    @abstractmethod
    async def get_invoice(
        self,
        invoice_id: UUID,
        current_user: User
    ) -> InvoiceResponse:
        """Get a specific invoice."""
        pass

    @abstractmethod
    async def search_invoices(
        self,
        client_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        is_overdue: Optional[bool] = None,
        current_user: User = None
    ) -> List[InvoiceResponse]:
        """Search and filter invoices."""
        pass

    @abstractmethod
    async def update_invoice(
        self,
        invoice_id: UUID,
        invoice_data: InvoiceUpdate,
        current_user: User
    ) -> InvoiceResponse:
        """Update an invoice."""
        pass

    @abstractmethod
    async def delete_invoice(
        self,
        invoice_id: UUID,
        current_user: User
    ) -> None:
        """Delete an invoice."""
        pass

    @abstractmethod
    async def get_overdue_invoices(
        self,
        current_user: User
    ) -> List[InvoiceResponse]:
        """Get all overdue invoices."""
        pass