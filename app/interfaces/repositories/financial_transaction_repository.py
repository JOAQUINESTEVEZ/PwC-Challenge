# interfaces/repository/financial_transaction_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from ...entities.financial_transaction import FinancialTransaction

class IFinancialTransactionRepository(ABC):
    @abstractmethod
    async def create(self, entity: FinancialTransaction) -> FinancialTransaction:
        """Create a new financial transaction."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[FinancialTransaction]:
        """Get a financial transaction by ID."""
        pass

    @abstractmethod
    async def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[FinancialTransaction]:
        """Retrieve all financial transactions for a specific client."""
        pass

    @abstractmethod
    async def search_transactions(
        self,
        client_id: Optional[UUID] = None,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None
    ) -> List[FinancialTransaction]:
        """Search transactions with filters."""
        pass

    @abstractmethod
    async def get_transactions_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[FinancialTransaction]:
        """Get all transactions within a specific date range."""
        pass

    @abstractmethod
    async def get_transactions_by_category(
        self,
        category: str
    ) -> List[FinancialTransaction]:
        """Get all transactions within a specific category."""
        pass

    @abstractmethod
    async def update(self, entity: FinancialTransaction) -> FinancialTransaction:
        """Update an existing financial transaction."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a financial transaction."""
        pass