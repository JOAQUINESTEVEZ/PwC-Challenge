from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID
from typing import Optional, List
from ...entities.invoice import InvoiceStatus

@dataclass(frozen=True)
class InvoiceDTO:
    id: UUID
    client_id: UUID
    amount_due: Decimal
    amount_paid: Decimal
    status: InvoiceStatus
    invoice_date: date
    due_date: date
    created_by: UUID

    @classmethod
    def from_entity(cls, entity):
        return cls(
            id=entity.id,
            client_id=entity.client_id,
            amount_due=entity.amount_due,
            amount_paid=entity.amount_paid,
            status=entity.status,
            invoice_date=entity.invoice_date,
            due_date=entity.due_date,
            created_by=entity.created_by
        )