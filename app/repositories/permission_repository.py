from typing import TypeVar, Type, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from .base_repository import BaseRepository
from ..models.permission_model import Permission
from ..schemas.permission_schema import PermissionCreate, PermissionUpdate

class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    """
    Repository for handling permission-related CRUD operations.
    """

    def get_permission(self, role_id: str, resource: str, action: str) -> Optional[Permission]:
        """
        Retrieve a specific permission by role_id, resource, and action.
        
        Args:
            role_id: The role ID
            resource: The resource name
            action: The action name (e.g., 'read', 'write')
        
        Returns:
            Optional[Permission]: The permission object or None
        """
        return self.db.query(Permission).filter_by(role_id=role_id, resource=resource, action=action).first()

