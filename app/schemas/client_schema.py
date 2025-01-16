from pydantic import BaseModel, EmailStr, UUID4, Field
from datetime import datetime
from typing import Optional

# Client Schemas
class ClientBase(BaseModel):
    name: str = Field(..., max_length=100)
    industry: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class Client(ClientBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True