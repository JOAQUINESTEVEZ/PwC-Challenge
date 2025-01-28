from ..base.user import UserBase
from datetime import datetime
from uuid import UUID

class UserResponse(UserBase):
    """Schema for user responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True