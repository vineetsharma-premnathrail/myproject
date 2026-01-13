
"""
Password Hashing Utilities Module
--------------------------------
Purpose:
    Provides secure password hashing and verification functions for user authentication.
    Ensures that user passwords are never stored in plain text.
Layer:
    Backend / Security / Authentication
"""

from passlib.context import CryptContext

# Password hashing context using bcrypt (industry standard for secure password storage)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Parameters:
        password (str): The plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hashed value.

    Parameters:
        plain_password (str): The plain text password to verify
        hashed_password (str): The hashed password to compare against

    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)