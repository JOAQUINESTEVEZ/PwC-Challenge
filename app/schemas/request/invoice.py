from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional
from decimal import Decimal
from ..base.invoice import InvoiceBase

class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice."""
    pass

class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    amount_due: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)
    amount_paid: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)

    @validator('amount_due')
    def validate_amount_due(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Amount due must be positive')
        return v

    @validator('amount_paid')
    def validate_amount_paid(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount paid cannot be negative')
        return v