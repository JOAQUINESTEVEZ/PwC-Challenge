from datetime import datetime, UTC
from uuid import UUID

from ..interfaces.services.audit_service import IAuditService
from ..interfaces.repositories.audit_log_repository import IAuditLogRepository
from ..entities.audit_log import AuditLog

class AuditService(IAuditService):
    def __init__(self, audit_log_repository: IAuditLogRepository):
        self.audit_log_repository = audit_log_repository
    
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