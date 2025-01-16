from pydantic import BaseModel, UUID4, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

# Financial Transaction Schemas
class FinancialTransactionBase(BaseModel):
    client_id: UUID4
    created_by: UUID4
    transaction_date: date
    amount: Decimal = Field(..., decimal_places=2, max_digits=15)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

class FinancialTransactionCreate(FinancialTransactionBase):
    pass

class FinancialTransactionUpdate(BaseModel):
    transaction_date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

class FinancialTransaction(FinancialTransactionBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True