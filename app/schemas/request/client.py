from ..base.client import ClientBase
from typing import Optional
from pydantic import EmailStr, Field

class ClientCreate(ClientBase):
    """Schema for client creation requests."""
    pass

class ClientUpdate(ClientBase):
    """Schema for client update requests."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    industry: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None