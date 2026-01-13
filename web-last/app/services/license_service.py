# License Service
# License key generation and activation logic

import secrets
import string
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
"""
License Service Module
----------------------
Purpose:
    Provides business logic for license key management, activation, and validation.
    Used by API endpoints and background tasks to control access to premium features.
Layer:
    Backend / Services / License
"""

from app.config import settings
import app.db.models as models


def generate_license_key(length: Optional[int] = None) -> str:
    """
    Generate a cryptographically secure random license key.

    Creates a random string using uppercase letters and digits.
    Uses secrets module for cryptographically strong randomness
    instead of random module (which is not suitable for security).

    Args:
        length (int, optional): Length of the license key. 
                               Defaults to settings.license_key_length.

    Returns:
        str: Randomly generated license key string (e.g., "A1B2C3D4E5F6")
    """
    if length is None:
        length = settings.license_key_length  # Get default length from app config

    characters = string.ascii_uppercase + string.digits  # Character set: A-Z and 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))  # Generate secure random string


def activate_license(license_key: str, user_id: int, db: Session):
    """
    Activate a license key for a specific user.

    This function performs several validation checks:
    1. Verifies the user exists
    2. Checks if the license key exists in the database
    3. Ensures the key hasn't been used before
    4. Updates both license and user records

    Args:
        license_key (str): The license key string to activate
        user_id (int): Database ID of the user activating the license
        db (Session): SQLAlchemy database session for transactions

    Returns:
        dict: Success message with activation confirmation

    Raises:
        HTTPException: 
            - 404 if user not found
            - 400 if license key is invalid or already used
    """
    # Step 1: Verify user exists in database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Find the license key record
    license_entry = db.query(models.LicenseKey).filter(
        models.LicenseKey.key == license_key
    ).first()

    if not license_entry:
        raise HTTPException(status_code=400, detail="Invalid License Key")

    # Step 3: Check if key is already used
    if license_entry.is_used:
        raise HTTPException(status_code=400, detail="Key already used")

    # Step 4: Activate the license
    license_entry.is_used = True  # Mark as used
    license_entry.used_at = func.now()  # Record activation timestamp
    license_entry.used_by_user_id = user_id  # Link to activating user
    license_entry.used_by_email = user.email  # Store email for reference

    # Step 5: Update user record
    user.is_license_active = True  # Enable premium features for user
    user.license_key = license_key  # Store key on user record

    # Step 6: Save all changes to database
    db.commit()

    return {"message": "License Activated!"}


def create_license_key(key_code: str, db: Session, expires_at=None):
    """
    Create a new license key record in the database.

    Used by administrators to add new license keys to the system
    that can later be distributed to users.

    Args:
        key_code (str): The license key string to create
        db (Session): Database session for the operation
        expires_at (datetime, optional): Expiration date for the key

    Returns:
        dict: Success message with creation confirmation

    Raises:
        HTTPException: If the key code already exists
    """
    # Check if key already exists to prevent duplicates
    existing = db.query(models.LicenseKey).filter(
        models.LicenseKey.key == key_code
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Key exists")

    # Create new license key record
    new_key = models.LicenseKey(key=key_code, expires_at=expires_at)
    db.add(new_key)  # Add to database session
    db.commit()  # Save to database

    return {"message": f"Key '{key_code}' created"}


def validate_license(user_id: int, db: Session) -> bool:
    """
    Check if a user's license is currently active.

    Used throughout the application to determine if a user
    has access to premium features and tools.

    Args:
        user_id (int): Database ID of the user to check
        db (Session): Database session for the query

    Returns:
        bool: True if user's license is active, False otherwise
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.is_license_active if user else False  # Return False if user doesn't exist


def is_license_valid(license_key: str, db: Session) -> bool:
    """
    Check whether a license key exists and is not used.

    Returns True if the license exists and `is_used` is False.
    """
    license_entry = db.query(models.LicenseKey).filter(models.LicenseKey.key == license_key).first()
    if not license_entry:
        return False
    return not bool(license_entry.is_used)