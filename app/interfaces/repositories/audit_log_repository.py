# interfaces/repository/audit_log_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ...entities.audit_log import AuditLog

class IAuditLogRepository(ABC):
    @abstractmethod
    async def create(self, entity: AuditLog) -> AuditLog:
        """Create a new audit log entry.
        
        Args:
            entity: Audit log entity to create
            
        Returns:
            AuditLog: Created audit log entity
            
        Raises:
            Exception: If creation fails
        """
        pass