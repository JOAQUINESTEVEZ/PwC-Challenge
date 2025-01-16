from pydantic import BaseModel, UUID4, Field
from datetime import datetime

# Audit Log Schemas
class AuditLogBase(BaseModel):
    changed_by: UUID4
    table_name: str = Field(..., max_length=50)
    record_id: UUID4
    change_type: str = Field(..., max_length=20)
    change_details: str

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: UUID4
    timestamp: datetime

    class Config:
        from_attributes = True