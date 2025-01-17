from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
from ..models.financial_transaction_model import FinancialTransaction
from ..schemas.financial_transaction_schema import FinancialTransactionCreate, FinancialTransactionUpdate
from .base_repository import BaseRepository

class FinancialTransactionRepository(BaseRepository[FinancialTransaction, FinancialTransactionCreate, FinancialTransactionUpdate]):
    """Repository for handling financial transaction database operations.

    This repository extends the BaseRepository to provide specific operations for
    financial transactions, including searching, filtering, and client-specific queries.

    Attributes:
        model: The SQLAlchemy model class for financial transactions
        db: SQLAlchemy database session
    """
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[FinancialTransaction]:
        """Retrieve all financial transactions for a specific client.

        Args:
            client_id (UUID): The unique identifier of the client
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            List[FinancialTransaction]: List of financial transactions for the specified client
        """
        return self.db.query(self.model)\
            .filter(self.model.client_id == client_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def search_transactions(self, 
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
        query = self.db.query(self.model)
        
        if client_id:
            query = query.filter(self.model.client_id == client_id)
            
        if category:
            query = query.filter(self.model.category == category)
            
        if start_date:
            query = query.filter(self.model.transaction_date >= start_date)
            
        if end_date:
            query = query.filter(self.model.transaction_date <= end_date)
            
        if min_amount is not None:
            query = query.filter(self.model.amount >= min_amount)
            
        if max_amount is not None:
            query = query.filter(self.model.amount <= max_amount)
            
        return query.all()

    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[FinancialTransaction]:
        """Retrieve transactions within a specific date range.

        Args:
            start_date (date): Start date of the range (inclusive)
            end_date (date): End date of the range (inclusive)

        Returns:
            List[FinancialTransaction]: List of transactions within the specified date range
        """
        return self.db.query(self.model)\
            .filter(self.model.transaction_date.between(start_date, end_date))\
            .all()

    def get_transactions_by_category(self, category: str) -> List[FinancialTransaction]:
        """Retrieve all transactions of a specific category.

        Args:
            category (str): Category to filter by

        Returns:
            List[FinancialTransaction]: List of transactions in the specified category
        """
        return self.db.query(self.model)\
            .filter(self.model.category == category)\
            .all()