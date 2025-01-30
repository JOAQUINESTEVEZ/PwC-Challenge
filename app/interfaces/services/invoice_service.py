# interfaces/service/invoice_service.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from ...entities.user import User
from ...schemas.dto.invoice_dto import InvoiceDTO

class IInvoiceService(ABC):
    @abstractmethod
    async def create_invoice(self, invoice_dto: InvoiceDTO, current_user: User) -> InvoiceDTO:
        """Create a new invoice."""
        pass

    @abstractmethod
    async def get_invoice(self, invoice_id: UUID) -> InvoiceDTO:
        """Get invoice by ID."""
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
        is_overdue: Optional[bool] = None
    ) -> List[InvoiceDTO]:
        """Search invoices with filters."""
        pass

    @abstractmethod
    async def update_invoice(self, invoice_dto: InvoiceDTO, current_user: User) -> InvoiceDTO:
        """Update an existing invoice."""
        pass

    @abstractmethod
    async def delete_invoice(self, invoice_id: UUID, current_user: User) -> None:
        """Delete an invoice."""
        pass

    @abstractmethod
    async def get_overdue_invoices(self, client_id: Optional[UUID] = None) -> List[InvoiceDTO]:
        """Get all overdue invoices."""
        pass