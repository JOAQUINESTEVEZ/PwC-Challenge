from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Dict, Any

class ChangeType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class Resource(str, Enum):
    CLIENT = "clients"
    INVOICE = "invoices"
    TRANSACTION = "financial_transactions"
    USER = "users"
    PERMISSION = "permissions"
    ROLE = "roles"

@dataclass
class AuditLog:
    """Entity representing an audit log entry with core business rules."""
    id: UUID
    changed_by: UUID
    table_name: Resource
    record_id: UUID
    change_type: ChangeType
    change_details: Dict[str, Any]  # Structured change data
    timestamp: datetime
    
    def __post_init__(self):
        """Validate business rules on creation."""
        self._validate_business_rules()
    
    def _validate_business_rules(self) -> None:
        """Enforce core business rules for audit logs."""
        # Rule: Timestamp cannot be in the future
        if self.timestamp > datetime.now():
            raise ValueError("Audit log timestamp cannot be in the future")
            
        # Rule: Change details must be provided for certain change types
        if self.change_type in [ChangeType.UPDATE, ChangeType.CREATE, ChangeType.DELETE] and not self.change_details:
            raise ValueError(f"{self.change_type} requires change details")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary format."""
        return {
            'id': str(self.id),
            'changed_by': str(self.changed_by),
            'table_name': self.resource.value,
            'record_id': str(self.record_id),
            'change_type': self.change_type.value,
            'change_details': self.change_details,
            'timestamp': self.timestamp.isoformat()
        }
