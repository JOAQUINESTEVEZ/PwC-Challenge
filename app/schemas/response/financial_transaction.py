from ..base.financial_transaction import FinancialTransactionBase
from datetime import datetime
from uuid import UUID

class FinancialTransactionResponse(FinancialTransactionBase):
    """Schema for financial transaction responses."""
    id: UUID
    created_by: UUID

    class Config:
        from_attributes = True