from ..base.financial_transaction import FinancialTransactionBase
from typing import Optional
from datetime import date
from decimal import Decimal

class FinancialTransactionCreate(FinancialTransactionBase):
    """Schema for financial transaction creation requests."""
    pass

class FinancialTransactionUpdate(FinancialTransactionBase):
    """Schema for financial transaction update requests."""
    transaction_date: Optional[date] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category: Optional[str] = None