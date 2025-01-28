from sqlalchemy.orm import Session
from typing import Optional
from ..repositories.permission_repository import PermissionRepository
from ..entities.permission import Permission

class PermissionService:
    """
    Service for handling permission-related business logic.
    """

    def __init__(self, db: Session):
        self.permission_repo = PermissionRepository(db)

    async def check_permission(self, role_id: str, resource: str, action: str) -> Optional[Permission]:
        """
        Check if the given role_id has the required resource and action permission.
        """
        permission_entity = await self.permission_repo.get_permission(role_id, resource, action)
        return permission_entity is not None