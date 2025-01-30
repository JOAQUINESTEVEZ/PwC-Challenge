# interfaces/repository/invoice_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from ...entities.invoice import Invoice

class IInvoiceRepository(ABC):
    @abstractmethod
    async def create(self, entity: Invoice) -> Invoice:
        """Create a new invoice."""
        pass

    @abstractmethod
    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get an invoice by ID."""
        pass

    @abstractmethod
    async def update(self, entity: Invoice) -> Invoice:
        """Update an existing invoice."""
        pass

    @abstractmethod
    async def delete(self, invoice_id: UUID) -> None:
        """Delete an invoice."""
        pass

    @abstractmethod
    async def search(
        self,
        client_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        is_overdue: Optional[bool] = None
    ) -> List[Invoice]:
        """Search invoices with filters."""
        pass

    @abstractmethod
    async def get_overdue(self, client_id: Optional[UUID] = None) -> List[Invoice]:
        """Get overdue invoices."""
        pass

    @abstractmethod
    async def get_by_client_id(self, client_id: UUID) -> List[Invoice]:
        """Get all invoices for a specific client."""
        pass