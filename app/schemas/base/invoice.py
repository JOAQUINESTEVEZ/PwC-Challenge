from pydantic import BaseModel, UUID4, Field, validator
from datetime import date
from decimal import Decimal

class InvoiceBase(BaseModel):
    """Base schema for invoice validation."""
    client_id: UUID4
    invoice_date: date
    due_date: date
    amount_due: Decimal = Field(..., decimal_places=2, max_digits=15)
    amount_paid: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=15)

    @validator('amount_due')
    def validate_amount_due(cls, v):
        """Validate amount due is positive."""
        if v <= 0:
            raise ValueError('Amount due must be positive')
        return v

    @validator('amount_paid')
    def validate_amount_paid(cls, v):
        """Validate amount paid is not negative."""
        if v < 0:
            raise ValueError('Amount paid cannot be negative')
        return v

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """Validate due date is after invoice date."""
        if 'invoice_date' in values and v < values['invoice_date']:
            raise ValueError('Due date cannot be before invoice date')
        return v