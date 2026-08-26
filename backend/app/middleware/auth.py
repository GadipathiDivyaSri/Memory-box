"""
Firebase Authentication Middleware
Verifies Firebase ID Tokens / JWT tokens and enforces strict 401 Unauthorized responses for invalid credentials.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from ..config import get_settings

logger = logging.getLogger("memorybox.auth_middleware")
settings = get_settings()
security = HTTPBearer(auto_error=False)


async def verify_firebase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict[str, Any]:
    """
    Verifies Firebase Authentication ID token.
    Returns 401 Unauthorized if missing, malformed, or invalid.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials.strip()

    # 1. Attempt Firebase Admin SDK verification if available
    try:
        import firebase_admin
        from firebase_admin import auth as firebase_auth

        # If Firebase is initialized, verify with Firebase Admin
        if firebase_admin._apps:
            try:
                decoded_token = firebase_auth.verify_id_token(token)
                return {
                    "uid": decoded_token.get("uid"),
                    "email": decoded_token.get("email"),
                    "name": decoded_token.get("name"),
                    "firebase": True,
                    "claims": decoded_token
                }
            except Exception as fe:
                logger.debug(f"Firebase token verification failed: {fe}")
    except ImportError:
        pass

    # 2. Verify with standard JWT secret key (HMAC SHA-256)
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub") or payload.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing required user identity claims.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return {
            "uid": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
            "role": payload.get("role", "owner"),
            "claims": payload
        }
    except JWTError as jwt_err:
        logger.warning(f"Invalid JWT Token provided: {jwt_err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(jwt_err)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> str:
    """Dependency that returns the authenticated user's UID or raises 401."""
    user_data = await verify_firebase_token(credentials)
    return user_data["uid"]
