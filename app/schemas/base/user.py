from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    """Base schema for user validation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role_id: UUID
    client_id: Optional[UUID] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v