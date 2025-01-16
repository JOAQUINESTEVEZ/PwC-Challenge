from pydantic import BaseModel, EmailStr, UUID4, Field
from datetime import datetime
from typing import Optional

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    role_id: Optional[UUID4] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[UUID4] = None

class User(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
