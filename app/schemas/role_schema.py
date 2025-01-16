from pydantic import BaseModel, UUID4, Field
from datetime import datetime

# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class Role(RoleBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True