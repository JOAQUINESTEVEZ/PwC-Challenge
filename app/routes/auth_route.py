from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..db import get_db
from ..controllers.auth_controller import AuthController
from ..schemas.request.login import LoginRequest
from ..schemas.request.signup import SignupRequest
from ..schemas.response.login import LoginResponse
from ..dependencies.auth import get_current_user

router = APIRouter()

@router.post("/login",
            response_model=LoginResponse,
            status_code=status.HTTP_200_OK,
            responses={
                401: {
                    "description": "Authentication failed",
                    "content": {
                        "application/json": {
                            "example": {
                                "type": "about:blank",
                                "title": "Authentication failed",
                                "status": 401,
                                "detail": "Incorrect username or password",
                                "instance": "/auth/login"
                            }
                        }
                    }
                }
            })
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Endpoint for user authentication and token generation.
    
    Args:
        form_data: OAuth2 form containing username and password
        db: Database session
        
    Returns:
        LoginResponse: Response containing access token
    """
    auth_controller = AuthController(db)
    return await auth_controller.login(form_data)

@router.post("/signup",
            response_model=LoginResponse,
            status_code=status.HTTP_201_CREATED,
            responses={
                400: {
                    "description": "Registration failed",
                    "content": {
                        "application/json": {
                            "example": {
                                "type": "about:blank",
                                "title": "Registration failed",
                                "status": 400,
                                "detail": "Username already exists",
                                "instance": "/auth/signup"
                            }
                        }
                    }
                }
            })
async def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Register a new client user and create corresponding client record.
    Returns an access token upon successful registration.
    """
    auth_controller = AuthController(db)
    return await auth_controller.signup(signup_data)

@router.get("/me",
            response_model=Dict[str, Any],
            status_code=status.HTTP_200_OK,
            responses={
                401: {
                    "description": "Not authenticated",
                    "content": {
                        "application/json": {
                            "example": {
                                "type": "about:blank",
                                "title": "Authentication required",
                                "status": 401,
                                "detail": "Not authenticated",
                                "instance": "/auth/me"
                            }
                        }
                    }
                }
            })
async def get_current_user(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Endpoint to get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from dependency
        db: Database session
        
    Returns:
        Dict[str, Any]: User information
    """
    auth_controller = AuthController(db)
    return await auth_controller.get_current_user_info(current_user)