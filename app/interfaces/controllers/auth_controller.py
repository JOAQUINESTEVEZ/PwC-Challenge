# interfaces/controller/auth_controller.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi.security import OAuth2PasswordRequestForm
from ...schemas.request.signup import SignupRequest
from ...schemas.response.login import LoginResponse

class IAuthController(ABC):
    @abstractmethod
    async def login(
        self,
        form_data: OAuth2PasswordRequestForm
    ) -> LoginResponse:
        """Handle user authentication and token generation."""
        pass

    @abstractmethod
    async def signup(
        self, 
        signup_data: SignupRequest
    ) -> LoginResponse:
        """Handle client signup process."""
        pass

    @abstractmethod
    async def get_current_user_info(
        self, 
        current_user: dict
    ) -> Dict[str, Any]:
        """Get current user information in API format."""
        pass