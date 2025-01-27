from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

@dataclass(frozen=True)
class TransactionDTO:
    """DTO for transaction list views and search results."""
    id: UUID
    client_id: UUID
    transaction_date: date
    amount: Decimal
    category: str
    description: str
    created_by: UUID

    @classmethod
    def from_entity(cls, entity):
        return cls(
            id=entity.id,
            client_id=entity.client_id,
            transaction_date=entity.transaction_date,
            amount=entity.amount,
            category=entity.category or "",
            description=entity.description or "",
            created_by=entity.created_by
        )
