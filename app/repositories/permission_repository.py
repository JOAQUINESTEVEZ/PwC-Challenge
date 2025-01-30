from typing import Optional
from sqlalchemy.orm import Session

from ..interfaces.repositories.permission_repository import IPermissionRepository
from ..models.permission_model import Permission as PermissionModel
from ..entities.permission import Permission

class PermissionRepository(IPermissionRepository):
    """
    Repository for handling permission-related CRUD operations.
    """
    def __init__(self, db: Session):
        """Initialize repository with db session."""
        self.db = db

    def _to_model(self, entity: Permission) -> PermissionModel:
        """Convert entity to model."""
        return PermissionModel(
            id=entity.id,
            role_id=entity.role_id,
            resource=entity.resource,
            action=entity.action,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _to_entity(self, model: PermissionModel) -> Permission:
        """Convert model to entity."""
        return Permission(
            id=model.id,
            role_id=model.role_id,
            resource=model.resource,
            action=model.action,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def get_permission(self, role_id: str, resource: str, action: str) -> Optional[Permission]:
        """
        Retrieve a specific permission by role_id, resource, and action.
        
        Args:
            role_id: The role ID
            resource: The resource name
            action: The action name (e.g., 'read', 'write')
        
        Returns:
            Optional[Permission]: The permission object or None
        """
        model = self.db.query(PermissionModel).filter_by(role_id=role_id, resource=resource, action=action).first()
        return self._to_entity(model) if model else None