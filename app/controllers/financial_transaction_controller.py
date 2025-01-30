from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException, status

from ..interfaces.controllers.financial_transaction_controller import IFinancialTransactionController
from ..interfaces.services.financial_transaction_service import IFinancialTransactionService
from ..entities.user import User
from ..schemas.request.financial_transaction import FinancialTransactionCreate, FinancialTransactionUpdate
from ..schemas.response.financial_transaction import FinancialTransactionResponse
from ..schemas.dto.transaction_dto import TransactionDTO

class FinancialTransactionController(IFinancialTransactionController):
    """
    Controller for managing financial transaction operations.
    Handles access control and coordinates between routes and services.
    """
    
    def __init__(self, transaction_service: IFinancialTransactionService):
        """
        Initialize controller with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.transaction_service = transaction_service

    def _check_transaction_access(self, transaction: TransactionDTO, current_user: User):
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
                             current_user: User) -> FinancialTransactionResponse:
        """Create a new financial transaction."""
        try:
            # Convert Request to DTO
            transaction_dto = TransactionDTO(
                id=None,
                client_id=transaction_data.client_id,
                transaction_date=transaction_data.transaction_date,
                amount=transaction_data.amount,
                category=transaction_data.category,
                description=transaction_data.description,
                created_by=current_user.id
            )
            
            # Send DTO to service, get DTO back
            result_dto = await self.transaction_service.create_transaction(transaction_dto, current_user)
            
            # Convert DTO to Response
            return FinancialTransactionResponse(
                id=result_dto.id,
                client_id=result_dto.client_id,
                transaction_date=result_dto.transaction_date,
                amount=result_dto.amount,
                category=result_dto.category,
                description=result_dto.description,
                created_by=result_dto.created_by
            )
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
                          current_user: User) -> FinancialTransactionResponse:
        """Retrieve a single transaction by ID."""
        try:
            result_dto = await self.transaction_service.get_transaction(transaction_id)
            self._check_transaction_access(result_dto, current_user)
            
            return FinancialTransactionResponse(
                id=result_dto.id,
                client_id=result_dto.client_id,
                transaction_date=result_dto.transaction_date,
                amount=result_dto.amount,
                category=result_dto.category,
                description=result_dto.description,
                created_by=result_dto.created_by
            )
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
                              current_user: User = None) -> List[FinancialTransactionResponse]:
        """Search for transactions with various filters."""
        try:
            # For client role, force client_id filter to their own id
            if current_user.role.name == "client":
                client_id = current_user.client_id
            
            result_dtos = await self.transaction_service.search_transactions(
                client_id=client_id,
                category=category,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount
            )

            # Convert DTOs to Responses
            return [
                FinancialTransactionResponse(
                    id=result_dto.id,
                    client_id=result_dto.client_id,
                    transaction_date=result_dto.transaction_date,
                    amount=result_dto.amount,
                    category=result_dto.category,
                    description=result_dto.description,
                    created_by=result_dto.created_by
                ) for result_dto in result_dtos
            ]
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
                             current_user: User) -> FinancialTransactionResponse:
        """Update an existing transaction."""
        try:
            # Convert Request to DTO
            update_dto = TransactionDTO(
                id=transaction_id,
                client_id=None, # Can't update client id
                transaction_date=transaction_data.transaction_date,
                amount=transaction_data.amount,
                category=transaction_data.category,
                description=transaction_data.description,
                created_by=None # Can't update created_by
            )

            # Send DTO to service, get DTO back
            result_dto = await self.transaction_service.update_transaction(update_dto, current_user)

            # Convert DTO to Response
            return FinancialTransactionResponse(
                id=result_dto.id,
                client_id=result_dto.client_id,
                transaction_date=result_dto.transaction_date,
                amount=result_dto.amount,
                category=result_dto.category,
                description=result_dto.description,
                created_by=result_dto.created_by
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
                             current_user: User) -> None:
        """Delete a transaction."""
        try: 
            await self.transaction_service.delete_transaction(transaction_id, current_user)
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