from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Permission:
    id: UUID
    role_id: UUID
    resource: str
    action: str
    created_at: datetime
    updated_at: datetime