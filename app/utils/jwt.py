from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from ..config import settings

def create_access_token(data: Dict[str, Any]) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "about:blank",
                "title": "Invalid authentication credentials",
                "status": 401,
                "detail": "Could not validate credentials",
                "instance": "/auth/token"
            }
        )
