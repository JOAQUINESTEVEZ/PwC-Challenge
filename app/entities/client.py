from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
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