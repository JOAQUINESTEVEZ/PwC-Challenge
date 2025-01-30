# interfaces/service/audit_service.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime

class IAuditService(ABC):
    @abstractmethod
    async def log_change(
        self,
        user_id: UUID,
        record_id: UUID,
        table_name: str,
        change_type: str,
        details: str
    ) -> None:
        """Log a change in the audit trail.
        
        Args:
            user_id: ID of the user making the change
            record_id: ID of the record being changed
            table_name: Name of the table being affected
            change_type: Type of change (CREATE, UPDATE, DELETE)
            details: Description of the change
            
        Raises:
            Exception: If logging fails
        """
        pass