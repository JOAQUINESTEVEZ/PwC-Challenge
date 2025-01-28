from ..base.audit_log import AuditLogBase
from datetime import datetime
from uuid import UUID

class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True