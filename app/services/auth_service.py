from typing import Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid
from ..repositories.user_repository import UserRepository
from ..repositories.client_repository import ClientRepository
from ..models.user_model import User
from ..models.client_model import Client
from ..schemas.auth_schema import LoginResponse
from ..schemas.signup_schema import SignupRequest
from ..utils.jwt import create_access_token
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(User, db)
        self.client_repository = ClientRepository(Client, db)
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[LoginResponse]:
        user = self.user_repository.get_by_username(username)
        if not user or not self.verify_password(password, user.password_hash):
            return None
            
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.name if user.role else None
        }
        
        access_token = create_access_token(token_data)
        return LoginResponse(access_token=access_token, token_type="bearer")

    def signup_client(self, signup_data: SignupRequest) -> LoginResponse:
        """
        Register a new client user and create corresponding client record.
        """
        # Check if username exists
        if self.user_repository.get_by_username(signup_data.username):
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
        if self.user_repository.get_by_email(signup_data.email):
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
        if self.client_repository.get_client_by_name(signup_data.company_name):
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
            # Create client record
            client = Client(
                id=uuid.uuid4(),
                name=signup_data.company_name,
                industry=signup_data.industry,
                contact_email=signup_data.contact_email,
                contact_phone=signup_data.contact_phone,
                address=signup_data.address,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            self.db.add(client)
            self.db.flush()  # Flush to get the client ID

            # Create user with client role
            client_role_id = "094f40bd-14de-48b0-8979-c8a7da41cab2"  # Client role ID
            hashed_password = pwd_context.hash(signup_data.password)
            
            user = User(
                id=uuid.uuid4(),
                username=signup_data.username,
                email=signup_data.email,
                password_hash=hashed_password,
                role_id=client_role_id,
                client_id=client.id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            self.db.add(user)
            self.db.commit()

            # Generate access token
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "role": "client",
                "client_id": str(client.id)
            }
            
            access_token = create_access_token(token_data)
            return LoginResponse(access_token=access_token, token_type="bearer")

        except Exception as e:
            self.db.rollback()
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