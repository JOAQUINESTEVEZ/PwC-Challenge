from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from dependency_injector.wiring import inject, Provide

from ..interfaces.controllers.auth_controller import IAuthController
from ..schemas.request.signup import SignupRequest
from ..schemas.response.login import LoginResponse
from ..dependencies.auth import get_current_user
from ..container import Container

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
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_controller: IAuthController = Depends(Provide[Container.auth_controller])
) -> LoginResponse:
    """
    Endpoint for user authentication and token generation.
    
    Args:
        form_data: OAuth2 form containing username and password
        db: Database session
        
    Returns:
        LoginResponse: Response containing access token
    """
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
@inject
async def signup(
    signup_data: SignupRequest,
    auth_controller: IAuthController = Depends(Provide[Container.auth_controller])
) -> LoginResponse:
    """
    Register a new client user and create corresponding client record.
    Returns an access token upon successful registration.
    """
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
@inject
async def get_current_user(
    current_user: dict = Depends(get_current_user),
    auth_controller: IAuthController = Depends(Provide[Container.auth_controller])
) -> Dict[str, Any]:
    """
    Endpoint to get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from dependency
        db: Database session
        
    Returns:
        Dict[str, Any]: User information
    """
    return await auth_controller.get_current_user_info(current_user)