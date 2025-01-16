from pydantic import BaseModel, UUID4, Field
from datetime import datetime

# Permission Schemas
class PermissionBase(BaseModel):
    role_id: UUID4
    resource: str = Field(..., max_length=50)
    action: str = Field(..., max_length=20)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True