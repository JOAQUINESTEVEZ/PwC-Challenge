from pydantic import UUID4
from datetime import datetime
from ...entities.invoice import InvoiceStatus
from ..base.invoice import InvoiceBase

class InvoiceResponse(InvoiceBase):
    """Schema for invoice responses."""
    id: UUID4
    created_by: UUID4
    status: InvoiceStatus

    class Config:
        from_attributes = True