# interfaces/service/auth_service.py
from abc import ABC, abstractmethod
from typing import Optional
from ...schemas.response.login import LoginResponse
from ...schemas.dto.client_dto import ClientDTO
from ...schemas.dto.user_dto import UserDTO

class IAuthService(ABC):
    @abstractmethod
    async def authenticate_user(
        self, 
        username: str, 
        password: str
    ) -> Optional[LoginResponse]:
        """Authenticate a user and generate access token."""
        pass

    @abstractmethod
    async def signup_client(
        self, 
        client_dto: ClientDTO, 
        user_dto: UserDTO
    ) -> LoginResponse:
        """Register a new client user and create client record."""
        pass

    @abstractmethod
    def verify_password(
        self, 
        plain_password: str, 
        hashed_password: str
    ) -> bool:
        """Verify if a plain password matches the hash."""
        pass