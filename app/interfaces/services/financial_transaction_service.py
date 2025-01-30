# interfaces/service/financial_transaction_service.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from ...entities.user import User
from ...schemas.dto.transaction_dto import TransactionDTO

class IFinancialTransactionService(ABC):
    @abstractmethod
    async def create_transaction(self, transaction_dto: TransactionDTO, current_user: User) -> TransactionDTO:
        """Create a new financial transaction."""
        pass

    @abstractmethod
    async def get_transaction(self, transaction_id: UUID) -> TransactionDTO:
        """Get transaction by ID."""
        pass

    @abstractmethod
    async def search_transactions(
        self,
        client_id: Optional[UUID] = None,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[TransactionDTO]:
        """Search transactions with filters."""
        pass

    @abstractmethod
    async def update_transaction(self, transaction_dto: TransactionDTO, current_user: User) -> TransactionDTO:
        """Update an existing transaction."""
        pass

    @abstractmethod
    async def delete_transaction(self, transaction_id: UUID, current_user: User) -> None:
        """Delete a transaction."""
        pass