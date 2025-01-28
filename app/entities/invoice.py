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