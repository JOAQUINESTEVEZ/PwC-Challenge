from pydantic import BaseModel, Field, validator
from datetime import date
from decimal import Decimal
from uuid import UUID
from typing import Optional

class FinancialTransactionBase(BaseModel):
    """Base schema for financial transaction validation."""
    client_id: UUID
    transaction_date: date
    amount: Decimal = Field(..., decimal_places=2, max_digits=15)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('transaction_date')
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError('Transaction date cannot be in the future')
        return v