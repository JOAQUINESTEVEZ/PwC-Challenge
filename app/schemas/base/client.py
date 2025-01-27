from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ClientBase(BaseModel):
    """Base schema for client validation."""
    name: str = Field(..., min_length=1, max_length=100)
    industry: str = Field(None, max_length=50)
    contact_email: EmailStr
    contact_phone: str = Field(None, max_length=50)
    address: str
