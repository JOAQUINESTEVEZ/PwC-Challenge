from ..base.user import UserBase
from pydantic import Field, Optional, EmailStr
from uuid import UUID

class UserCreate(UserBase):
    """Schema for user creation requests."""
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    """Schema for user update requests."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    password: Optional[str] = Field(None, min_length=8)
