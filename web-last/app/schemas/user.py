"""
User Schemas Module
------------------
Purpose:
    Defines Pydantic models for user-related data structures.
    Provides validation and serialization for user profiles, updates,
    and responses throughout the application.
Layer:
    Backend / Schemas / User Management
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base user model with essential user information.

    Contains the minimum required fields for user identification and status.
    Used as a foundation for other user-related schemas.

    Attributes:
        email: User's email address (primary identifier)
        is_license_active: Whether user has an active license (default: False)
    """
    email: EmailStr
    is_license_active: bool = False


class UserResponse(UserBase):
    """
    Standard user response model for API endpoints.

    Extends UserBase with the user ID for complete user identification.
    Used when returning user information in API responses.

    Attributes:
        id: Unique user identifier
        email: User's email address
        is_license_active: License activation status
    """
    id: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema for updating user account information.

    Allows partial updates to user email and license status.
    All fields are optional to support selective updates.

    Attributes:
        email: New email address (optional)
        is_license_active: New license status (optional)
    """
    email: Optional[EmailStr] = None
    is_license_active: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    """
    Schema for updating user profile information.

    Contains fields that users can modify in their profile settings.
    All fields are optional for flexible profile updates.

    Attributes:
        name: User's display name
        phone_number: User's contact phone number
        profile_photo_path: Path to user's profile photo
    """
    name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_photo_path: Optional[str] = None


class UserProfile(UserResponse):
    """
    Extended user profile model with complete user information.

    Includes all user data for detailed profile views and admin panels.
    Combines basic user info with profile details and account metadata.

    Attributes:
        id: Unique user identifier
        email: User's email address
        is_license_active: License activation status
        name: User's display name
        phone_number: User's contact phone number
        profile_photo_path: Path to user's profile photo
        license_key: Associated license key (if any)
        is_manager: Whether user has manager privileges
        created_at: Account creation timestamp
        last_login: Last login timestamp
    """
    name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_photo_path: Optional[str] = None
    license_key: Optional[str] = None
    is_manager: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None