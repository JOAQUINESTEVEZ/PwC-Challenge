from sqlalchemy.orm import Session
from ..repositories.permission_repository import PermissionRepository
from ..models.permission_model import Permission
from ..schemas.permission_schema import PermissionCreate, PermissionUpdate

class PermissionService:
    """
    Service for handling permission-related business logic.
    """

    def __init__(self, db: Session):
        self.permission_repo = PermissionRepository(Permission, db)

    def check_permission(self, role_id: str, resource: str, action: str) -> bool:
        """
        Check if the given role_id has the required resource and action permission.
        """
        permission = self.permission_repo.get_permission(role_id, resource, action)
        return permission is not None