from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class UserDTO:
    """DTO for authentication and authorization."""
    id: UUID
    username: str
    email: str
    password_hash: str
    role_id: UUID
    client_id: UUID

    @classmethod
    def from_entity(cls, entity):
        return cls(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            role_id=entity.role_id,
            client_id=entity.client_id
        )