from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, UTC

from ..interfaces.repositories.financial_transaction_repository import IFinancialTransactionRepository
from ..interfaces.services.financial_transaction_service import IFinancialTransactionService
from ..interfaces.services.audit_service import IAuditService
from ..entities.user import User
from ..entities.financial_transaction import FinancialTransaction
from ..schemas.dto.transaction_dto import TransactionDTO
from decimal import Decimal

class FinancialTransactionService(IFinancialTransactionService):
    """
    Service for handling financial transaction business logic.
    Manages transaction operations and business rules.
    """
    
    def __init__(self, transaction_repository: IFinancialTransactionRepository, audit_service: IAuditService):
        """
        Initialize service with database session.
        
        Args:
            db: Database session
        """
        self.transaction_repository = transaction_repository
        self.audit_service = audit_service

    async def create_transaction(self, transaction_dto: TransactionDTO, current_user: User) -> TransactionDTO:
        """
        Create a new financial transaction.
        
        Args:
            transaction_dto: Data for transaction creation
            current_user: User creating the transaction
            
        Returns:
            TransactionDTO: Created transaction
        """
        try:
            # Convert DTO to entity
            transaction_entity = FinancialTransaction(
                id=None,
                client_id=transaction_dto.client_id,
                created_by=transaction_dto.created_by,
                transaction_date=transaction_dto.transaction_date,
                amount=transaction_dto.amount,
                category=transaction_dto.category,
                description=transaction_dto.description,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

            # Save through repository
            saved_transaction = await self.transaction_repository.create(transaction_entity)

            # Create Log
            await self.audit_service.log_change(
                user_id=current_user.id,
                record_id=saved_transaction.id,
                table_name="financial_transactions",
                change_type="CREATE",
                details=f"Created financial transaction for client {saved_transaction.client_id}"
            )

            # Convert entity to DTO
            return TransactionDTO.from_entity(saved_transaction)
        
        except Exception as e:
            raise ValueError(f"Error creating transaction: {str(e)}")
        
    async def get_transaction(self, transaction_id: UUID) -> TransactionDTO:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: UUID of transaction to retrieve
            
        Returns:
            TransactionDTO: Found transaction
            
        Raises:
            ValueError: If transaction not found
        """
        transaction = await self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction with id '{transaction_id}' not found")
            
        return TransactionDTO.from_entity(transaction)

    async def search_transactions(self,
                        client_id: Optional[UUID] = None,
                        category: Optional[str] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        min_amount: Optional[float] = None,
                        max_amount: Optional[float] = None) -> List[TransactionDTO]:
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
            List[TransactionDTO]: List of matching transactions
            
        Raises:
            ValueError: If date range is invalid
        """
        try:
            if start_date and end_date and end_date < start_date:
                raise ValueError("End date cannot be before start date")
            
            # Convert amounts to Decimal if provided
            min_amount_decimal = Decimal(str(min_amount)) if min_amount is not None else None
            max_amount_decimal = Decimal(str(max_amount)) if max_amount is not None else None

            # Get filtered transactions
            transactions = await self.transaction_repository.search_transactions(
                client_id=client_id,
                category=category,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount_decimal,
                max_amount=max_amount_decimal
            )

            # Convert to DTOs
            return [
                TransactionDTO.from_entity(transaction)
                for transaction in transactions
            ]
        
        except Exception as e:
            raise ValueError(f"Error searching transactions: {str(e)}")

    async def update_transaction(self, 
                       transaction_dto: TransactionDTO,
                       current_user: User) -> TransactionDTO:
        """
        Update an existing transaction.
        
        Args:
            transaction_dto: Updated transaction data
            current_user: User performing the update
            
        Returns:
            TransactionDTO: Updated transaction
            
        Raises:
            ValueError: If transaction not found or validation fails
        """
        try:
            # Get existing transaction
            existing_transaction = await self.transaction_repository.get_by_id(transaction_dto.id)
            if not existing_transaction:
                raise ValueError(f"Transaction with id {transaction_dto.id} not found")
            
            # Update fields while preserving others
            if transaction_dto.amount:
                existing_transaction.amount = transaction_dto.amount
            if transaction_dto.category:
                existing_transaction.category = transaction_dto.category
            if transaction_dto.description:
                existing_transaction.description = transaction_dto.description
            if transaction_dto.transaction_date:
                existing_transaction.transaction_date = transaction_dto.transaction_date

            # Apply business rules
            existing_transaction.validate_amount()
            existing_transaction.validate_dates()
            existing_transaction.updated_at = datetime.now(UTC)

            # Save updates
            updated_transaction = await self.transaction_repository.update(existing_transaction)

            # Create Log
            await self.audit_service.log_change(
                user_id=current_user.id,
                record_id=updated_transaction.id,
                table_name="financial_transactions",
                change_type="UPDATE",
                details=f"Updated financial transaction for client {updated_transaction.client_id}"
            )

            # Convert entity to DTO and return
            return TransactionDTO.from_entity(updated_transaction)

        except Exception as e:
            raise ValueError(f"Error updating transaction: {str(e)}")

    async def delete_transaction(self, transaction_id: UUID, current_user: User) -> None:
        """
        Delete a transaction.
        
        Args:
            transaction_id: UUID of transaction to delete
            current_user: User performing the deletion
        """
        # Verify transaction exists
        transaction = await self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction with id {transaction_id} not found")
        
        await self.transaction_repository.delete(transaction_id)

        # Create Log
        await self.audit_service.log_change(
            user_id=current_user.id,
            record_id=transaction_id,
            table_name="financial_transactions",
            change_type="DELETE",
            details=f"Deleted financial transaction for client {transaction.client_id}"
        )