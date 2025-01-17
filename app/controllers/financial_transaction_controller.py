from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from ..services.financial_transaction_service import FinancialTransactionService
from ..models.user_model import User
from ..schemas.financial_transaction_schema import (
    FinancialTransaction,
    FinancialTransactionCreate,
    FinancialTransactionUpdate
)

class FinancialTransactionController:
    """Controller for managing financial transaction operations.

    This controller handles the coordination between the HTTP layer and the service layer
    for all financial transaction operations. It manages request validation, response
    formatting, and error handling.

    Attributes:
        transaction_service (FinancialTransactionService): Service for transaction operations
    """
    
    def __init__(self, db: Session):
        """Initialize controller with database session.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.transaction_service = FinancialTransactionService(db)

    async def create_transaction(self, 
                             transaction_data: FinancialTransactionCreate,
                             current_user: User) -> FinancialTransaction:
        """Create a new financial transaction.

        Args:
            transaction_data (FinancialTransactionCreate): Data for new transaction
            current_user (User): Currently authenticated user

        Returns:
            FinancialTransaction: Created transaction

        Raises:
            HTTPException: If creation fails or validation errors occur
        """
        return self.transaction_service.create_transaction(transaction_data, current_user)

    async def get_transaction(self,
                          transaction_id: UUID,
                          current_user: User) -> FinancialTransaction:
        """Retrieve a single transaction by ID.

        Args:
            transaction_id (UUID): ID of transaction to retrieve
            current_user (User): Currently authenticated user

        Returns:
            FinancialTransaction: Retrieved transaction

        Raises:
            HTTPException: If transaction not found or user lacks permission
        """
        return self.transaction_service.get_transaction(transaction_id, current_user)

    async def search_transactions(self,
                              client_id: Optional[UUID] = None,
                              category: Optional[str] = None,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              min_amount: Optional[float] = None,
                              max_amount: Optional[float] = None,
                              current_user: User = None) -> List[FinancialTransaction]:
        """Search for transactions with various filters.

        Args:
            client_id (Optional[UUID], optional): Filter by client. Defaults to None.
            category (Optional[str], optional): Filter by category. Defaults to None.
            start_date (Optional[date], optional): Start date range. Defaults to None.
            end_date (Optional[date], optional): End date range. Defaults to None.
            min_amount (Optional[float], optional): Minimum amount. Defaults to None.
            max_amount (Optional[float], optional): Maximum amount. Defaults to None.
            current_user (User, optional): Currently authenticated user. Defaults to None.

        Returns:
            List[FinancialTransaction]: List of matching transactions
        """
        return self.transaction_service.search_transactions(
            client_id=client_id,
            category=category,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            current_user=current_user
        )

    async def update_transaction(self,
                             transaction_id: UUID,
                             transaction_data: FinancialTransactionUpdate,
                             current_user: User) -> FinancialTransaction:
        """Update an existing transaction.

        Args:
            transaction_id (UUID): ID of transaction to update
            transaction_data (FinancialTransactionUpdate): Updated transaction data
            current_user (User): Currently authenticated user

        Returns:
            FinancialTransaction: Updated transaction

        Raises:
            HTTPException: If transaction not found or user lacks permission
        """
        return self.transaction_service.update_transaction(
            transaction_id,
            transaction_data,
            current_user
        )

    async def delete_transaction(self,
                             transaction_id: UUID,
                             current_user: User) -> bool:
        """Delete a transaction.

        Args:
            transaction_id (UUID): ID of transaction to delete
            current_user (User): Currently authenticated user

        Returns:
            bool: True if successful, False otherwise

        Raises:
            HTTPException: If transaction not found or user lacks permission
        """
        return self.transaction_service.delete_transaction(transaction_id, current_user)