# interfaces/repository/permission_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from ...entities.permission import Permission

class IPermissionRepository(ABC):
    @abstractmethod
    async def get_permission(
        self, 
        role_id: str, 
        resource: str, 
        action: str
    ) -> Optional[Permission]:
        """
        Retrieve a specific permission by role_id, resource, and action.
        
        Args:
            role_id: The role ID
            resource: The resource name
            action: The action name (e.g., 'read', 'write')
            
        Returns:
            Optional[Permission]: The found permission or None
        """
        pass