from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.orm import Session
from ..repositories.audit_log_repository import AuditLogRepository
from ..entities.audit_log import AuditLog

class AuditService:
    def __init__(self, db: Session):
        self.audit_log_repository = AuditLogRepository(db)
    
    async def log_change(
        self,
        user_id: UUID,
        record_id: UUID,
        table_name: str,
        change_type: str,
        details: str
    ) -> None:
        audit_log = AuditLog(
            id=None,
            changed_by=user_id,
            table_name=table_name,
            record_id=record_id,
            change_type=change_type,
            change_details=details,
            timestamp=datetime.now(UTC)
        )
        
        await self.audit_log_repository.create(audit_log)