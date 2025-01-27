from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class User:
    id: UUID
    username: str
    email: str
    password_hash: str
    role_id: UUID
    role: str
    client_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        self.validate_username()
        self.validate_email()

    def validate_username(self) -> None:
        """Validate username."""
        if len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters long")

    def validate_email(self) -> None:
        """Validate email format."""
        if '@' not in self.email or '.' not in self.email:
            raise ValueError("Invalid email format")

    def update_details(self, username: Optional[str] = None,
                      email: Optional[str] = None,
                      role_id: Optional[UUID] = None) -> None:
        """Update user details with validation."""
        if username is not None:
            self.username = username
            self.validate_username()
        if email is not None:
            self.email = email
            self.validate_email()
        if role_id is not None:
            self.role_id = role_id
        self.updated_at = datetime.now()