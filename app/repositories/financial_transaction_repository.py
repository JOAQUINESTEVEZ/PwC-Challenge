from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import date
from ..models.financial_transaction_model import FinancialTransaction as FinancialTransactionModel
from ..entities.financial_transaction import FinancialTransaction

class FinancialTransactionRepository:
    """Repository for handling financial transaction database operations.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def _to_model(self, entity: FinancialTransaction) -> FinancialTransactionModel:
        """Convert entity to model."""
        return FinancialTransactionModel(
            id=entity.id,
            client_id=entity.client_id,
            created_by=entity.created_by,
            transaction_date=entity.transaction_date,
            amount=entity.amount,
            description=entity.description,
            category=entity.category,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _to_entity(self, model:FinancialTransactionModel) -> FinancialTransaction:
        """Convert model to entity."""
        return FinancialTransaction(
            id=model.id,
            client_id=model.client_id,
            created_by=model.created_by,
            transaction_date=model.transaction_date,
            amount=model.amount,
            description=model.description,
            category=model.category,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def create(self, entity: FinancialTransaction) -> FinancialTransaction:
        """Create a new financial transaction in the database."""
        try:
            model = self._to_model(entity)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error creating financial transaction: {str(e)}")
        
    async def get_by_id(self, id: UUID) -> Optional[FinancialTransaction]:
        """Get a financial transaction by ID."""
        model = self.db.query(FinancialTransactionModel).filter(FinancialTransactionModel.id == id).first()
        return self._to_entity(model) if model else None
    
    async def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[FinancialTransaction]:
        """Retrieve all financial transactions for a specific client.

        Args:
            client_id (UUID): The unique identifier of the client
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            List[FinancialTransaction]: List of financial transactions for the specified client
        """
        models = self.db.query(FinancialTransactionModel)\
            .filter(FinancialTransactionModel.client_id == client_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return [self._to_entity(model) for model in models]

    async def search_transactions(self, 
                        client_id: Optional[UUID] = None,
                        category: Optional[str] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        min_amount: Optional[float] = None,
                        max_amount: Optional[float] = None) -> List[FinancialTransaction]:
        """Search and filter financial transactions based on multiple criteria.

        Args:
            client_id (UUID, optional): Filter by client ID. Defaults to None.
            category (str, optional): Filter by transaction category. Defaults to None.
            start_date (date, optional): Filter transactions after this date. Defaults to None.
            end_date (date, optional): Filter transactions before this date. Defaults to None.
            min_amount (float, optional): Filter transactions with amount >= this value. Defaults to None.
            max_amount (float, optional): Filter transactions with amount <= this value. Defaults to None.

        Returns:
            List[FinancialTransaction]: List of transactions matching the specified criteria
        """
        query = self.db.query(FinancialTransactionModel)
        
        if client_id:
            query = query.filter(FinancialTransactionModel.client_id == client_id)
            
        if category:
            query = query.filter(FinancialTransactionModel.category == category)
            
        if start_date:
            query = query.filter(FinancialTransactionModel.transaction_date >= start_date)
            
        if end_date:
            query = query.filter(FinancialTransactionModel.transaction_date <= end_date)
            
        if min_amount is not None:
            query = query.filter(FinancialTransactionModel.amount >= min_amount)
            
        if max_amount is not None:
            query = query.filter(FinancialTransactionModel.amount <= max_amount)
            
        models = query.all()
        return [self._to_entity(model) for model in models]

    async def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[FinancialTransaction]:
        """Retrieve transactions within a specific date range.

        Args:
            start_date (date): Start date of the range (inclusive)
            end_date (date): End date of the range (inclusive)

        Returns:
            List[FinancialTransaction]: List of transactions within the specified date range
        """
        models = self.db.query(FinancialTransactionModel)\
            .filter(FinancialTransactionModel.transaction_date.between(start_date, end_date))\
            .all()
        return [self._to_entity(model) for model in models]

    async def get_transactions_by_category(self, category: str) -> List[FinancialTransaction]:
        """Retrieve all transactions of a specific category.

        Args:
            category (str): Category to filter by

        Returns:
            List[FinancialTransaction]: List of transactions in the specified category
        """
        models = self.db.query(FinancialTransactionModel)\
            .filter(FinancialTransactionModel.category == category)\
            .all()
        return [self._to_entity(model) for model in models]
    
    async def update(self, entity: FinancialTransaction) -> FinancialTransaction:
        """Update an existing financial transaction."""
        try:
            model = self._to_model(entity)
            self.db.merge(model)
            self.db.commit()
            
            # Refresh and return updated entity
            updated_model = self.db.query(FinancialTransactionModel).filter(FinancialTransactionModel.id == entity.id).first()
            return self._to_entity(updated_model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error updating financial transaction: {str(e)}")

    async def delete(self, id: UUID) -> None:
        """Delete a financial transaction."""
        try:
            model = self.db.query(FinancialTransactionModel).filter(FinancialTransactionModel.id == id).first()
            if model:
                self.db.delete(model)
                self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error deleting financial transaction: {str(e)}")