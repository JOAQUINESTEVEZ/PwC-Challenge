from pydantic import BaseModel, UUID4, Field, model_validator
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from enum import Enum

class InvoiceStatus(str, Enum):
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"

class InvoiceBase(BaseModel):
    client_id: UUID4
    invoice_date: date
    due_date: date
    amount_due: Decimal = Field(..., decimal_places=2, max_digits=15)
    amount_paid: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=15)
    status: InvoiceStatus = Field(default=InvoiceStatus.PENDING)

    @model_validator(mode='after')
    def validate_amounts_and_status(self) -> 'InvoiceBase':
        if self.amount_paid > self.amount_due:
            raise ValueError('Amount paid cannot exceed amount due')
            
        if self.amount_paid == self.amount_due:
            self.status = InvoiceStatus.PAID
        elif self.amount_paid > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID
        else:
            self.status = InvoiceStatus.PENDING
            
        return self
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'InvoiceBase':
        if self.due_date < self.invoice_date:
            raise ValueError('Due date cannot be before invoice date')
        return self

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    amount_due: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)
    amount_paid: Optional[Decimal] = Field(None, decimal_places=2, max_digits=15)
    status: Optional[InvoiceStatus] = None

class Invoice(InvoiceBase):
    id: UUID4
    created_by: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True