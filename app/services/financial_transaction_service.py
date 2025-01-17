from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, UTC
from sqlalchemy.orm import Session
from ..models.financial_transaction_model import FinancialTransaction
from ..models.user_model import User
from ..repositories.financial_transaction_repository import FinancialTransactionRepository
from ..schemas.financial_transaction_schema import FinancialTransactionCreate, FinancialTransactionUpdate
from ..models.audit_logs_model import AuditLog
from decimal import Decimal

class FinancialTransactionService:
    """
    Service for handling financial transaction business logic.
    Manages transaction operations and business rules.
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: Database session
        """
        self.transaction_repository = FinancialTransactionRepository(FinancialTransaction, db)
        self.db = db

    def _create_audit_log(self, user_id: UUID, record_id: UUID, change_type: str, details: str) -> None:
        """
        Create an audit log entry for transaction changes.
        
        Args:
            user_id: ID of user making the change
            record_id: ID of affected transaction
            change_type: Type of change (create, update, delete)
            details: Change details
        """
        audit_log = AuditLog(
            changed_by=user_id,
            table_name="financial_transactions",
            record_id=record_id,
            change_type=change_type,
            change_details=details,
            timestamp=datetime.now(UTC)
        )
        self.db.add(audit_log)
        self.db.commit()

    def _validate_transaction_amount(self, amount: Decimal) -> None:
        """
        Validate transaction amount.
        
        Args:
            amount: Transaction amount to validate
            
        Raises:
            ValueError: If amount is invalid
        """
        if amount <= Decimal('0'):
            raise ValueError("Transaction amount must be positive")

    def create_transaction(self, transaction_data: FinancialTransactionCreate, current_user: User) -> FinancialTransaction:
        """
        Create a new financial transaction.
        
        Args:
            transaction_data: Data for transaction creation
            current_user: User creating the transaction
            
        Returns:
            FinancialTransaction: Created transaction
            
        Raises:
            ValueError: If validation fails
        """
        # Validate amount
        self._validate_transaction_amount(transaction_data.amount)
        
        # Create transaction
        transaction_dict = transaction_data.model_dump()
        transaction_dict["created_by"] = current_user.id
        
        transaction = self.transaction_repository.create(transaction_dict)
        
        # Create audit log
        self._create_audit_log(
            user_id=current_user.id,
            record_id=transaction.id,
            change_type="create",
            details=f"Created transaction of {transaction.amount} for client {transaction.client_id}"
        )
        
        return transaction

    def get_transaction(self, transaction_id: UUID) -> FinancialTransaction:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: UUID of transaction to retrieve
            
        Returns:
            FinancialTransaction: Found transaction
            
        Raises:
            ValueError: If transaction not found
        """
        transaction = self.transaction_repository.get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction with id '{transaction_id}' not found")
            
        return transaction

    def search_transactions(self,
                        client_id: Optional[UUID] = None,
                        category: Optional[str] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        min_amount: Optional[float] = None,
                        max_amount: Optional[float] = None) -> List[FinancialTransaction]:
        """
        Search transactions with filters.
        
        Args:
            client_id: Optional client filter
            category: Optional category filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            min_amount: Optional minimum amount filter
            max_amount: Optional maximum amount filter
            
        Returns:
            List[FinancialTransaction]: List of matching transactions
            
        Raises:
            ValueError: If date range is invalid
        """
        # Validate date range
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date cannot be before start date")
            
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
        """
        Update an existing transaction.
        
        Args:
            transaction_id: UUID of transaction to update
            transaction_data: Updated transaction data
            current_user: User performing the update
            
        Returns:
            FinancialTransaction: Updated transaction
            
        Raises:
            ValueError: If transaction not found or validation fails
        """
        # Check if transaction exists
        transaction = self.get_transaction(transaction_id)
        
        # Validate amount if provided
        if transaction_data.amount is not None:
            self._validate_transaction_amount(transaction_data.amount)
        
        updated_transaction = self.transaction_repository.update(transaction_id, transaction_data)
        
        # Create audit log
        self._create_audit_log(
            user_id=current_user.id,
            record_id=transaction_id,
            change_type="update",
            details=f"Updated transaction {transaction_id}"
        )
        
        return updated_transaction

    def delete_transaction(self, transaction_id: UUID, current_user: User) -> bool:
        """
        Delete a transaction.
        
        Args:
            transaction_id: UUID of transaction to delete
            current_user: User performing the deletion
            
        Returns:
            bool: True if deleted, False if not found
        """
        # Verify transaction exists
        transaction = self.get_transaction(transaction_id)
        
        result = self.transaction_repository.delete(transaction_id)
        
        if result:
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                record_id=transaction_id,
                change_type="delete",
                details=f"Deleted transaction {transaction_id}"
            )
            
        return result