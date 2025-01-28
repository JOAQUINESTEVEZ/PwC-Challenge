from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
    
@dataclass(frozen=True)
class ClientDTO:
    """DTO for detailed client operations."""
    id: UUID
    name: str
    industry: str
    contact_email: str
    contact_phone: str
    address: str

    @classmethod
    def from_entity(cls, entity):
        return cls(
            id=entity.id,
            name=entity.name,
            industry=entity.industry or "",
            contact_email=entity.contact_email or "",
            contact_phone=entity.contact_phone or "",
            address=entity.address or ""
        )