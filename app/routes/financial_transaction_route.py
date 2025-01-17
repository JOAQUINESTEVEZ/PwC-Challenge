from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..controllers.financial_transaction_controller import FinancialTransactionController
from ..schemas.financial_transaction_schema import (
    FinancialTransaction,
    FinancialTransactionCreate,
    FinancialTransactionUpdate
)
from ..dependencies.auth import get_current_user, check_permissions
from ..models.user_model import User

router = APIRouter()

@router.post("",
            response_model=FinancialTransaction,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(check_permissions("financial_transactions", "create"))],
            responses={
                401: {"description": "Not authenticated"},
                403: {"description": "Not enough permissions"},
                404: {"description": "Client not found"}
            })
async def create_transaction(
    transaction_data: FinancialTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FinancialTransaction:
    """Create a new financial transaction."""
    controller = FinancialTransactionController(db)
    return await controller.create_transaction(transaction_data, current_user)

@router.get("/{transaction_id}",
           response_model=FinancialTransaction,
           dependencies=[Depends(check_permissions("financial_transactions", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Transaction not found"}
           })
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FinancialTransaction:
    """Get a specific financial transaction by ID."""
    controller = FinancialTransactionController(db)
    return await controller.get_transaction(transaction_id, current_user)

@router.get("",
           response_model=List[FinancialTransaction],
           dependencies=[Depends(check_permissions("financial_transactions", "read"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"}
           })
async def search_transactions(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[FinancialTransaction]:
    """Search and filter financial transactions."""
    controller = FinancialTransactionController(db)
    return await controller.search_transactions(
        client_id=client_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        current_user=current_user
    )

@router.put("/{transaction_id}",
           response_model=FinancialTransaction,
           dependencies=[Depends(check_permissions("financial_transactions", "update"))],
           responses={
               401: {"description": "Not authenticated"},
               403: {"description": "Not enough permissions"},
               404: {"description": "Transaction not found"}
           })
async def update_transaction(
    transaction_id: UUID,
    transaction_data: FinancialTransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FinancialTransaction:
    """Update an existing financial transaction."""
    controller = FinancialTransactionController(db)
    return await controller.update_transaction(transaction_id, transaction_data, current_user)

@router.delete("/{transaction_id}",
             status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(check_permissions("financial_transactions", "delete"))],
             responses={
                 401: {"description": "Not authenticated"},
                 403: {"description": "Not enough permissions"},
                 404: {"description": "Transaction not found"}
             })
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a financial transaction."""
    controller = FinancialTransactionController(db)
    result = await controller.delete_transaction(transaction_id, current_user)
    
    if not result:
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