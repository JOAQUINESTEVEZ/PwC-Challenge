from typing import Optional
from sqlalchemy.orm import Session

from ..interfaces.repositories.permission_repository import IPermissionRepository
from ..models.permission_model import Permission as PermissionModel
from ..entities.permission import Permission
from ..interfaces.repositories.cache_repository import ICacheRepository

class PermissionRepository(IPermissionRepository):
    """
    Repository for handling permission-related CRUD operations.
    """
    def __init__(self, db: Session, cache: ICacheRepository):
        """Initialize repository with db session."""
        self.db = db
        self.cache = cache
        # Longer TTL for permissions as they rarely change
        self.permission_ttl = 86400 * 30  # 30 days

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
        # Create cache key
        cache_key = f"perm:{role_id}:{resource}:{action}"
        
        # Try to get from cache
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return Permission.from_dict(cached_data)

        # Get from database if not in cache
        model = self.db.query(PermissionModel).filter(
            PermissionModel.role_id == role_id,
            PermissionModel.resource == resource,
            PermissionModel.action == action
        ).first()

        if not model:
            # Cache negative result to prevent repeated DB queries
            # Use shorter TTL for negative results
            await self.cache.set(cache_key, None, ttl=300)  # 5 minutes
            return None

        # Convert to entity
        permission = self._to_entity(model)
        
        # Cache the result
        await self.cache.set(
            cache_key, 
            permission.to_dict(),
            ttl=self.permission_ttl
        )
        
        return permission