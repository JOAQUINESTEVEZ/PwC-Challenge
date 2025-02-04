from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from enum import Enum

class InvoiceStatus(str, Enum):
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"

@dataclass
class Invoice:
    id: UUID
    client_id: UUID
    created_by: UUID
    invoice_date: date
    due_date: date
    amount_due: Decimal
    amount_paid: Decimal
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        self.validate_amounts()
        self.validate_dates()
        self.update_status()

    def validate_amounts(self) -> None:
        """Validate invoice amounts."""
        if self.amount_due <= Decimal('0'):
            raise ValueError("Invoice amount must be positive")
        if self.amount_paid < Decimal('0'):
            raise ValueError("Paid amount cannot be negative")
        if self.amount_paid > self.amount_due:
            raise ValueError("Paid amount cannot exceed amount due")

    def validate_dates(self) -> None:
        """Validate invoice dates."""
        if self.due_date < self.invoice_date:
            raise ValueError("Due date cannot be before invoice date")

    def update_status(self) -> None:
        """Update invoice status based on amounts."""
        if self.amount_paid >= self.amount_due:
            self.status = InvoiceStatus.PAID
        elif self.amount_paid > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID
        else:
            self.status = InvoiceStatus.PENDING

    def record_payment(self, payment_amount: Decimal) -> None:
        """Record a payment with validation."""
        if payment_amount <= Decimal('0'):
            raise ValueError("Payment amount must be positive")
        if self.amount_paid + payment_amount > self.amount_due:
            raise ValueError("Payment would exceed amount due")
        if self.status == InvoiceStatus.PAID:
            raise ValueError("Invoice is already paid")
            
        self.amount_paid += payment_amount
        self.update_status()
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        return self.due_date < date.today() and self.status != InvoiceStatus.PAID

    def can_be_deleted(self) -> bool:
        """Check if invoice can be deleted."""
        return self.status != InvoiceStatus.PAID
    
    def to_dict(self) -> dict:
        """Convert invoice to dictionary for serialization."""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "created_by": str(self.created_by),
            "invoice_date": self.invoice_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "amount_due": str(self.amount_due),
            "amount_paid": str(self.amount_paid),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Create invoice from dictionary."""
        return cls(
            id=UUID(data["id"]) if data["id"] else None,
            client_id=UUID(data["client_id"]),
            created_by=UUID(data["created_by"]),
            invoice_date=date.fromisoformat(data["invoice_date"]),
            due_date=date.fromisoformat(data["due_date"]),
            amount_due=Decimal(data["amount_due"]),
            amount_paid=Decimal(data["amount_paid"]),
            status=InvoiceStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )