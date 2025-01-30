from typing import Optional

from ..interfaces.services.permission_service import IPermissionService
from ..interfaces.repositories.permission_repository import IPermissionRepository
from ..entities.permission import Permission

class PermissionService(IPermissionService):
    """
    Service for handling permission-related business logic.
    """

    def __init__(self, permission_repository: IPermissionRepository):
        self.permission_repository = permission_repository

    async def check_permission(self, role_id: str, resource: str, action: str) -> Optional[Permission]:
        """
        Check if the given role_id has the required resource and action permission.
        """
        permission_entity = await self.permission_repository.get_permission(role_id, resource, action)
        return permission_entity is not None