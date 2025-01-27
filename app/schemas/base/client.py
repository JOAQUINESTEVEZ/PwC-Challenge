from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ClientBase(BaseModel):
    """Base schema for client validation."""
    name: str = Field(..., min_length=1, max_length=100)
    industry: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
