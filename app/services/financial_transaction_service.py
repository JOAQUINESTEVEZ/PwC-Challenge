from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.financial_transaction_model import FinancialTransaction
from ..models.user_model import User
from ..repositories.financial_transaction_repository import FinancialTransactionRepository
from ..schemas.financial_transaction_schema import FinancialTransactionCreate, FinancialTransactionUpdate
from ..models.audit_logs_model import AuditLog

class FinancialTransactionService:
    """Service for handling financial transaction business logic.

    This service implements the business logic for financial transactions,
    including creation, retrieval, updates, and deletions. It handles
    permissions, validations, and audit logging.

    Attributes:
        transaction_repository (FinancialTransactionRepository): Repository for database operations
        db (Session): Database session
    """
    
    def __init__(self, db: Session):
        """Initialize service with database session.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.transaction_repository = FinancialTransactionRepository(FinancialTransaction, db)
        self.db = db

    def create_transaction(self, 
                       transaction_data: FinancialTransactionCreate, 
                       current_user: User) -> FinancialTransaction:
        """Create a new financial transaction.

        Args:
            transaction_data (FinancialTransactionCreate): Transaction data to create
            current_user (User): Currently authenticated user

        Returns:
            FinancialTransaction: Created transaction

        Raises:
            HTTPException: If validation fails or insufficient permissions
        """
        # Convert Pydantic model to dict and add created_by
        transaction_dict = transaction_data.model_dump()
        transaction_dict["created_by"] = current_user.id
        
        transaction = self.transaction_repository.create(transaction_dict)
        
        # Create audit log
        audit_log = AuditLog(
            changed_by=current_user.id,
            table_name="financial_transactions",
            record_id=transaction.id,
            change_type="create",
            change_details=f"Created financial transaction of {transaction.amount} for client {transaction.client_id}"
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return transaction

    def get_transaction(self, 
                     transaction_id: UUID, 
                     current_user: User) -> FinancialTransaction:
        """Retrieve a transaction by ID.

        Args:
            transaction_id (UUID): Transaction ID to retrieve
            current_user (User): Currently authenticated user

        Returns:
            FinancialTransaction: Retrieved transaction

        Raises:
            HTTPException: If transaction not found or insufficient permissions
        """
        transaction = self.transaction_repository.get(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Transaction not found",
                    "status": 404,
                    "detail": f"Transaction with id '{transaction_id}' not found",
                    "instance": f"/finance/transactions/{transaction_id}"
                }
            )
        
        # If user is a client, they can only view their own transactions
        if current_user.role.name == "client" and transaction.client_id != current_user.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Access denied",
                    "status": 403,
                    "detail": "You can only view your own transactions",
                    "instance": f"/finance/transactions/{transaction_id}"
                }
            )
            
        return transaction

    def search_transactions(self,
                        client_id: Optional[UUID] = None,
                        category: Optional[str] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        min_amount: Optional[float] = None,
                        max_amount: Optional[float] = None,
                        current_user: User = None) -> List[FinancialTransaction]:
        """Search transactions with various filters.

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
        # If user is a client, force client_id filter to their own id
        if current_user.role.name == "client":
            client_id = current_user.client_id
            
        return self.transaction_repository.search_transactions(
            client_id=client_id,
            category=category,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount
        )

    def update_transaction(self, 
                       transaction_id: UUID, 
                       transaction_data: FinancialTransactionUpdate,
                       current_user: User) -> FinancialTransaction:
        """Update an existing transaction.

        Args:
            transaction_id (UUID): Transaction ID to update
            transaction_data (FinancialTransactionUpdate): Updated transaction data
            current_user (User): Currently authenticated user

        Returns:
            FinancialTransaction: Updated transaction

        Raises:
            HTTPException: If transaction not found or insufficient permissions
        """
        # Check if transaction exists
        transaction = self.get_transaction(transaction_id, current_user)
        
        updated_transaction = self.transaction_repository.update(transaction_id, transaction_data)
        
        # Create audit log
        audit_log = AuditLog(
            changed_by=current_user.id,
            table_name="financial_transactions",
            record_id=transaction_id,
            change_type="update",
            change_details=f"Updated financial transaction {transaction_id}"
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return updated_transaction

    def delete_transaction(self, 
                       transaction_id: UUID,
                       current_user: User) -> bool:
        """Delete a transaction.

        Args:
            transaction_id (UUID): Transaction ID to delete
            current_user (User): Currently authenticated user

        Returns:
            bool: True if successful, False otherwise

        Raises:
            HTTPException: If transaction not found or insufficient permissions
        """
        # Check if transaction exists
        transaction = self.get_transaction(transaction_id, current_user)
        
        result = self.transaction_repository.delete(transaction_id)
        
        if result:
            # Create audit log
            audit_log = AuditLog(
                changed_by=current_user.id,
                table_name="financial_transactions",
                record_id=transaction_id,
                change_type="delete",
                change_details=f"Deleted financial transaction {transaction_id}"
            )
            self.db.add(audit_log)
            self.db.commit()
            
        return result