# interfaces/service/permission_service.py
from abc import ABC, abstractmethod
from typing import Optional
from ...entities.permission import Permission

class IPermissionService(ABC):
    @abstractmethod
    async def check_permission(
        self, 
        role_id: str, 
        resource: str, 
        action: str
    ) -> bool:
        """
        Check if the given role_id has the required resource and action permission.
        
        Args:
            role_id: The role ID to check
            resource: The resource being accessed
            action: The action being performed
            
        Returns:
            bool: True if permission exists, False otherwise
        """
        pass