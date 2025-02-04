from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Dict

@dataclass
class Permission:
    id: UUID
    role_id: UUID
    resource: str
    action: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict:
        """Convert permission to dictionary for caching."""
        return {
            "id": str(self.id),
            "role_id": str(self.role_id),
            "resource": self.resource,
            "action": self.action,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Permission':
        """Create permission from dictionary."""
        return cls(
            id=UUID(data["id"]),
            role_id=UUID(data["role_id"]),
            resource=data["resource"],
            action=data["action"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )