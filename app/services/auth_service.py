from typing import Optional
from datetime import datetime, UTC
from passlib.context import CryptContext
from fastapi import HTTPException, status

from ..interfaces.services.auth_service import IAuthService
from ..interfaces.repositories.user_repository import IUserRepository
from ..interfaces.repositories.client_repository import IClientRepository
from ..interfaces.services.audit_service import IAuditService
from ..entities.user import User
from ..entities.client import Client
from ..schemas.response.login import LoginResponse
from ..schemas.dto.client_dto import ClientDTO
from ..schemas.dto.user_dto import UserDTO
from ..utils.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService(IAuthService):
    def __init__(self, user_repository: IUserRepository, client_repository: IClientRepository, audit_service: IAuditService):
        self.user_repository = user_repository
        self.client_repository = client_repository
        self.audit_service = audit_service

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, username: str, password: str) -> Optional[LoginResponse]:
        user = await self.user_repository.get_by_username(username)
        if not user or not self.verify_password(password, user.password_hash):
            return None
            
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.name if user.role else None
        }
        
        access_token = create_access_token(token_data)
        return LoginResponse(access_token=access_token, token_type="bearer")

    async def signup_client(self, client_dto:ClientDTO, user_dto:UserDTO) -> LoginResponse:
        """
        Register a new client user and create corresponding client record.
        """
        # Check if username exists
        if await self.user_repository.get_by_username(user_dto.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Username already exists",
                    "status": 400,
                    "detail": "This username is already taken",
                    "instance": "/auth/signup"
                }
            )

        # Check if email exists
        if await self.user_repository.get_by_email(user_dto.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Email already exists",
                    "status": 400,
                    "detail": "This email is already registered",
                    "instance": "/auth/signup"
                }
            )

        # Check if company name exists
        if await self.client_repository.get_client_by_name(client_dto.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "about:blank",
                    "title": "Company already exists",
                    "status": 400,
                    "detail": "A client with this company name already exists",
                    "instance": "/auth/signup"
                }
            )

        try:
            # Convert DTO to entity
            client_entity = Client(
                id=None,
                name=client_dto.name,
                industry=client_dto.industry,
                contact_email=client_dto.contact_email,
                contact_phone=client_dto.contact_phone,
                address=client_dto.address,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

            # Save through repository
            saved_client_entity = await self.client_repository.create(client_entity)

            hashed_password = pwd_context.hash(user_dto.password_hash)
            # Create user with client role
            client_role_id = "094f40bd-14de-48b0-8979-c8a7da41cab2"  # Client role ID

            user_entity = User(
                id=None,
                username=user_dto.username,
                email=user_dto.email,
                password_hash=hashed_password,
                role_id=client_role_id,
                role="client",
                client_id=saved_client_entity.id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

            # Save through repository
            saved_user_entity = await self.user_repository.create(user_entity)
            
            # Generate access token
            token_data = {
                "sub": str(saved_user_entity.id),
                "username": saved_user_entity.username,
                "role": "client",
                "client_id": str(saved_user_entity.client_id)
            }
            
            access_token = create_access_token(token_data)

            # Create Logs
            await self.audit_service.log_change(
                user_id=None,
                record_id=saved_client_entity.id,
                table_name="clients",
                change_type="CREATE",
                details=f"Created client {saved_client_entity.name}"
            )
            await self.audit_service.log_change(
                user_id=None,
                record_id=saved_user_entity.id,
                table_name="users",
                change_type="CREATE",
                details=f"Created user {saved_user_entity.username}"
            )

            return LoginResponse(access_token=access_token, token_type="bearer")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "type": "about:blank",
                    "title": "Registration failed",
                    "status": 500,
                    "detail": str(e),
                    "instance": "/auth/signup"
                }
            )