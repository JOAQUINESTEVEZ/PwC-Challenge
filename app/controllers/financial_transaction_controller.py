from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..services.financial_transaction_service import FinancialTransactionService
from ..models.user_model import User
from ..schemas.financial_transaction_schema import (
    FinancialTransaction,
    FinancialTransactionCreate,
    FinancialTransactionUpdate
)

class FinancialTransactionController:
    """
    Controller for managing financial transaction operations.
    Handles access control and coordinates between routes and services.
    """
    
    def __init__(self, db: Session):
        """
        Initialize controller with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.transaction_service = FinancialTransactionService(db)

    def _check_transaction_access(self, transaction: FinancialTransaction, current_user: User):
        """
        Check if user has access to transaction.
        
        Args:
            transaction: Transaction to check
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If access is denied
        """
        if current_user.role.name == "client" and transaction.client_id != current_user.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Access denied",
                    "status": 403,
                    "detail": "You can only access your own transactions",
                    "instance": f"/finance/transactions/{transaction.id}"
                }
            )

    async def create_transaction(self, 
                             transaction_data: FinancialTransactionCreate,
                             current_user: User) -> FinancialTransaction:
        """Create a new financial transaction."""
        try:
            # For client role, ensure they can only create transactions for themselves
            if current_user.role.name == "client":
                if str(transaction_data.client_id) != str(current_user.client_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "type": "about:blank",
                            "title": "Access denied",
                            "status": 403,
                            "detail": "You can only create transactions for your own account",
                            "instance": "/finance/transactions"
                        }
                    )
            
            return self.transaction_service.create_transaction(transaction_data, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid transaction data",
                    "status": 400,
                    "detail": str(e),
                    "instance": "/finance/transactions"
                }
            )

    async def get_transaction(self,
                          transaction_id: UUID,
                          current_user: User) -> FinancialTransaction:
        """Retrieve a single transaction by ID."""
        try:
            transaction = self.transaction_service.get_transaction(transaction_id)
            self._check_transaction_access(transaction, current_user)
            return transaction
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Transaction not found",
                    "status": 404,
                    "detail": str(e),
                    "instance": f"/finance/transactions/{transaction_id}"
                }
            )

    async def search_transactions(self,
                              client_id: Optional[UUID] = None,
                              category: Optional[str] = None,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              min_amount: Optional[float] = None,
                              max_amount: Optional[float] = None,
                              current_user: User = None) -> List[FinancialTransaction]:
        """Search for transactions with various filters."""
        try:
            # For client role, force client_id filter to their own id
            if current_user.role.name == "client":
                client_id = current_user.client_id
            
            return self.transaction_service.search_transactions(
                client_id=client_id,
                category=category,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid search parameters",
                    "status": 400,
                    "detail": str(e),
                    "instance": "/finance/transactions"
                }
            )

    async def update_transaction(self,
                             transaction_id: UUID,
                             transaction_data: FinancialTransactionUpdate,
                             current_user: User) -> FinancialTransaction:
        """Update an existing transaction."""
        try:
            # First get the transaction to check access
            transaction = self.transaction_service.get_transaction(transaction_id)
            self._check_transaction_access(transaction, current_user)
            
            return self.transaction_service.update_transaction(
                transaction_id,
                transaction_data,
                current_user
            )
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "type": "about:blank",
                        "title": "Transaction not found",
                        "status": 404,
                        "detail": str(e),
                        "instance": f"/finance/transactions/{transaction_id}"
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Invalid update data",
                    "status": 400,
                    "detail": str(e),
                    "instance": f"/finance/transactions/{transaction_id}"
                }
            )

    async def delete_transaction(self,
                             transaction_id: UUID,
                             current_user: User) -> bool:
        """Delete a transaction."""
        try:
            # First get the transaction to check access
            transaction = self.transaction_service.get_transaction(transaction_id)
            self._check_transaction_access(transaction, current_user)
            
            return self.transaction_service.delete_transaction(transaction_id, current_user)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "type": "about:blank",
                        "title": "Transaction not found",
                        "status": 404,
                        "detail": str(e),
                        "instance": f"/finance/transactions/{transaction_id}"
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Delete operation failed",
                    "status": 400,
                    "detail": str(e),
                    "instance": f"/finance/transactions/{transaction_id}"
                }
            )