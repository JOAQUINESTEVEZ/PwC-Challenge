from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict
from uuid import UUID
from enum import Enum

@dataclass
class Client:
    id: UUID
    name: str
    industry: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict:
        """Convert entity to dictionary for serialization."""
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "industry": self.industry,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Client':
        """Create entity from dictionary."""
        return cls(
            id=UUID(data["id"]) if data["id"] else None,
            name=data["name"],
            industry=data["industry"],
            contact_email=data["contact_email"],
            contact_phone=data["contact_phone"],
            address=data["address"],
            created_at=datetime.fromisoformat(data["created_at"]) if data["created_at"] else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else None
        )

    def update_details(self, name: Optional[str] = None, industry: Optional[str] = None,
                      contact_email: Optional[str] = None, contact_phone: Optional[str] = None,
                      address: Optional[str] = None) -> None:
        """Update client details with validation."""
        if name is not None:
            if len(name.strip()) == 0:
                raise ValueError("Client name cannot be empty")
            self.name = name
        if industry is not None:
            self.industry = industry
        if contact_email is not None:
            self.contact_email = contact_email
        if contact_phone is not None:
            self.contact_phone = contact_phone
        if address is not None:
            self.address = address
        self.updated_at = datetime.now()