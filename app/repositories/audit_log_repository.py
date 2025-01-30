from sqlalchemy.orm import Session

from ..interfaces.repositories.audit_log_repository import IAuditLogRepository
from ..models.audit_logs_model import AuditLog as AuditLogModel
from ..entities.audit_log import AuditLog

class AuditLogRepository(IAuditLogRepository):
    """
    Repository for AuditLog-specific database operations.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def _to_model(self, entity: AuditLog) -> AuditLogModel:
        """Convert entity to model."""
        return AuditLogModel(
            id=entity.id,
            changed_by=entity.changed_by,
            table_name=entity.table_name,
            record_id=entity.record_id,
            change_type=entity.change_type,
            change_details=entity.change_details,
            timestamp=entity.timestamp
        )
    
    def _to_entity(self, model: AuditLogModel) -> AuditLog:
        """Convert model to entity."""
        return AuditLog(
            id=model.id,
            changed_by=model.changed_by,
            table_name=model.table_name,
            record_id=model.record_id,
            change_type=model.change_type,
            change_details=model.change_details,
            timestamp=model.timestamp
        )
    
    async def create(self, entity: AuditLog) -> AuditLog:
        """Create a new audit log in the database."""
        try:
            model = self._to_model(entity)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Failed to create audit log: {str(e)}")