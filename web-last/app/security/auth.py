
"""
Authentication Security Module
-----------------------------
Purpose:
    Provides JWT token creation, verification, and user extraction utilities for secure authentication.
    Used to manage stateless authentication for API endpoints.
Layer:
    Backend / Security / Authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token for a user.

    Parameters:
        data (dict): The payload data to encode in the token (e.g., user info)
        expires_delta (timedelta, optional): Token expiry duration. Defaults to config value.

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Parameters:
        token (str): The JWT token to verify

    Returns:
        dict or None: The decoded payload if valid, else None
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        # Token is invalid or expired
        return None

def get_current_user(token: str) -> Optional[dict]:
    """
    Extract user information from a JWT token.

    Parameters:
        token (str): The JWT token

    Returns:
        dict or None: User info (e.g., user_id) if token is valid, else None
    """
    payload = verify_token(token)
    if payload:
        return {"user_id": payload.get("sub")}
    return None