from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from enum import Enum

@dataclass
class FinancialTransaction:
    id: UUID
    client_id: UUID
    created_by: UUID
    transaction_date: date
    amount: Decimal
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        self.validate_amount()
        self.validate_dates()

    def validate_amount(self) -> None:
        """Validate transaction amount."""
        if self.amount <= Decimal('0'):
            raise ValueError("Transaction amount must be positive")

    def validate_dates(self) -> None:
        """Validate transaction dates."""
        if self.transaction_date > date.today():
            raise ValueError("Transaction date cannot be in the future")

    def update_details(self, amount: Optional[Decimal] = None,
                      description: Optional[str] = None,
                      category: Optional[str] = None,
                      transaction_date: Optional[date] = None) -> None:
        """Update transaction details with validation."""
        if amount is not None:
            self.amount = amount
            self.validate_amount()
        if description is not None:
            self.description = description
        if category is not None:
            self.category = category
        if transaction_date is not None:
            self.transaction_date = transaction_date
            self.validate_dates()
        self.updated_at = datetime.now()