from pydantic import BaseModel, UUID4, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

# Invoice Schemas
class InvoiceBase(BaseModel):
    client_id: UUID4
    created_by: UUID4
    invoice_date: date
    due_date: date
    amount_due: Decimal = Field(..., decimal_places=2, max_digits=15)
    amount_paid: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=15)
    status: str = Field(..., max_length=20)

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    amount_due: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)
    amount_paid: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)
    status: Optional[str] = Field(None, max_length=20)

class Invoice(InvoiceBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True