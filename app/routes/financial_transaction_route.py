from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from ..interfaces.controllers.financial_transaction_controller import IFinancialTransactionController
from ..schemas.request.financial_transaction import FinancialTransactionCreate, FinancialTransactionUpdate
from ..schemas.response.financial_transaction import FinancialTransactionResponse
from ..entities.user import User
from ..dependencies.auth import get_current_user, check_permissions
from ..container import Container

router = APIRouter()

@router.post("",
            response_model=FinancialTransactionResponse,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(check_permissions("financial_transactions", "create"))],
            responses={
                401: {"description": "Not authenticated"},
                403: {"description": "Not enough permissions"},
                404: {"description": "Client not found"},
                400: {"description": "Invalid transaction data"}
            })
@inject
async def create_transaction(
    transaction_data: FinancialTransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_controller: IFinancialTransactionController = Depends(Provide[Container.transaction_controller])
) -> FinancialTransactionResponse:
    """
    Create a new financial transaction.

    Args:
        transaction_data: Data for the new transaction
        current_user: Current authenticated user
        db: Database session

    Returns:
        FinancialTransactionResponse: Created transaction

    Raises:
        HTTPException: If creation fails or permissions not met
    """
    return await transaction_controller.create_transaction(transaction_data, current_user)

@router.get("/{transaction_id}",
           response_model=FinancialTransactionResponse,
           dependencies=[Depends(check_permissions("financial_transactions", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Transaction not found"}
           })
@inject
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_controller: IFinancialTransactionController = Depends(Provide[Container.transaction_controller])
) -> FinancialTransactionResponse:
    """
    Get a specific financial transaction by ID.

    Args:
        transaction_id: UUID of transaction to retrieve
        current_user: Current authenticated user
        db: Database session

    Returns:
        FinancialTransactionResponse: Retrieved transaction

    Raises:
        HTTPException: If transaction not found or access denied
    """
    return await transaction_controller.get_transaction(transaction_id, current_user)

@router.get("",
           response_model=List[FinancialTransactionResponse],
           dependencies=[Depends(check_permissions("financial_transactions", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"}
           })
@inject
async def search_transactions(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    current_user: User = Depends(get_current_user),
    transaction_controller: IFinancialTransactionController = Depends(Provide[Container.transaction_controller])
) -> List[FinancialTransactionResponse]:
    """
    Search and filter financial transactions.

    Args:
        client_id: Optional client ID filter
        category: Optional category filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        min_amount: Optional minimum amount filter
        max_amount: Optional maximum amount filter
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[FinancialTransactionResponse]: List of matching transactions
    """
    return await transaction_controller.search_transactions(
        client_id=client_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        current_user=current_user
    )

@router.put("/{transaction_id}",
           response_model=FinancialTransactionResponse,
           dependencies=[Depends(check_permissions("financial_transactions", "update"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Transaction not found"},
               400: {"description": "Invalid update data"}
           })
@inject
async def update_transaction(
    transaction_id: UUID,
    transaction_data: FinancialTransactionUpdate,
    current_user: User = Depends(get_current_user),
    transaction_controller: IFinancialTransactionController = Depends(Provide[Container.transaction_controller])
) -> FinancialTransactionResponse:
    """
    Update an existing financial transaction.

    Args:
        transaction_id: UUID of transaction to update
        transaction_data: Updated transaction data
        current_user: Current authenticated user
        db: Database session

    Returns:
        FinancialTransactionResponse: Updated transaction

    Raises:
        HTTPException: If transaction not found or update fails
    """
    return await transaction_controller.update_transaction(transaction_id, transaction_data, current_user)

@router.delete("/{transaction_id}",
             status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(check_permissions("financial_transactions", "delete"))],
             responses={
                 401: {"description": "Not authenticated"},
                 403: {"description": "Not enough permissions"},
                 404: {"description": "Transaction not found"}
             })
@inject
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_controller: IFinancialTransactionController = Depends(Provide[Container.transaction_controller])
):
    """
    Delete a financial transaction.

    Args:
        transaction_id: UUID of transaction to delete
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If transaction not found or deletion fails
    """
    await transaction_controller.delete_transaction(transaction_id, current_user)
    return None