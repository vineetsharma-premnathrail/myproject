"""
Authentication Schemas Module
----------------------------
Purpose:
    Defines Pydantic models for authentication-related API requests and responses.
    Provides data validation and serialization for user registration, login,
    license activation, and token management operations.
Layer:
    Backend / Schemas / Authentication
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for user registration requests.

    Used when new users sign up for the application.
    Validates email format and ensures password is provided.

    Attributes:
        email: User's email address (must be valid email format)
        password: User's chosen password (plain text, will be hashed)
        name: User's full name (optional)
        license_key: License key for activation (optional, for legacy signup)
    """
    email: EmailStr
    password: str
    name: Optional[str] = None
    license_key: Optional[str] = None


class UserLogin(BaseModel):
    """
    Schema for user login requests.

    Used when existing users attempt to authenticate.
    Validates email format and ensures password is provided.

    Attributes:
        email: User's registered email address
        password: User's password (plain text, will be verified against hash)
    """
    email: EmailStr
    password: str


class LicenseActivate(BaseModel):
    """
    Schema for license key activation requests.

    Used when users activate their license keys to gain full access.

    Attributes:
        license_key: The license key string provided by the user
    """
    license_key: str


class TokenResponse(BaseModel):
    """
    Schema for authentication token responses.

    Returned after successful login or token refresh operations.
    Contains the JWT token and metadata for client-side storage.

    Attributes:
        access_token: The JWT access token string
        token_type: Token type (always "bearer" for JWT)
        expires_in: Token expiration time in seconds
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int