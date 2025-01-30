# interfaces/controller/financial_transaction_controller.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from ...entities.user import User
from ...schemas.request.financial_transaction import FinancialTransactionCreate, FinancialTransactionUpdate
from ...schemas.response.financial_transaction import FinancialTransactionResponse

class IFinancialTransactionController(ABC):
    @abstractmethod
    async def create_transaction(
        self,
        transaction_data: FinancialTransactionCreate,
        current_user: User
    ) -> FinancialTransactionResponse:
        """Create a new transaction."""
        pass

    @abstractmethod
    async def get_transaction(
        self,
        transaction_id: UUID,
        current_user: User
    ) -> FinancialTransactionResponse:
        """Get a specific transaction."""
        pass

    @abstractmethod
    async def search_transactions(
        self,
        client_id: Optional[UUID] = None,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        current_user: User = None
    ) -> List[FinancialTransactionResponse]:
        """Search and filter transactions."""
        pass

    @abstractmethod
    async def update_transaction(
        self,
        transaction_id: UUID,
        transaction_data: FinancialTransactionUpdate,
        current_user: User
    ) -> FinancialTransactionResponse:
        """Update a transaction."""
        pass

    @abstractmethod
    async def delete_transaction(
        self,
        transaction_id: UUID,
        current_user: User
    ) -> None:
        """Delete a transaction."""
        pass