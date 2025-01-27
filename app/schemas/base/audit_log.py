from pydantic import BaseModel
from uuid import UUID
from typing import Any, Dict
from datetime import datetime
from enum import Enum

class ChangeType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class AuditLogBase(BaseModel):
    """Base schema for audit log validation."""
    changed_by: UUID
    table_name: str
    record_id: UUID
    change_type: ChangeType
    change_details: Dict[str, Any]