from ..base.client import ClientBase
from datetime import datetime
from uuid import UUID

class ClientResponse(ClientBase):
    """Schema for client responses."""
    id: UUID

    class Config:
        from_attributes = True