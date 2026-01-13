
"""
Custom Exceptions Module
-----------------------
Purpose:
    Defines application-specific exception classes for consistent error handling across the backend.
    Used to raise meaningful, structured errors for validation, authentication, authorization, and external service issues.
Layer:
    Backend / Utilities / Error Handling
"""

from fastapi import HTTPException
from typing import Any, Dict, Optional

class AppException(HTTPException):
    """
    Base application exception for all custom errors.

    Responsibility:
        Serves as the parent for all custom exceptions in the app, ensuring a consistent error structure.
    When/Why:
        Use as a base for all domain-specific exceptions to standardize error responses.
    """
    def __init__(self, status_code: int, detail: str, headers: Optional[Dict[str, Any]] = None):
        """
        Initialize the base application exception.

        Parameters:
            status_code (int): HTTP status code for the error.
            detail (str): Human-readable error message.
            headers (dict, optional): Additional HTTP headers.
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class ValidationError(AppException):
    """
    Exception for input validation errors.

    Responsibility:
        Raised when user input fails validation checks.
    When/Why:
        Use in API endpoints or services to indicate invalid input data.
    """
    def __init__(self, detail: str):
        """
        Initialize a validation error.

        Parameters:
            detail (str): Description of the validation failure.
        """
        super().__init__(status_code=400, detail=f"Validation error: {detail}")

class AuthenticationError(AppException):
    """
    Exception for authentication failures.

    Responsibility:
        Raised when user authentication fails (e.g., invalid credentials).
    When/Why:
        Use in login or protected endpoints to signal authentication problems.
    """
    def __init__(self, detail: str = "Authentication failed"):
        """
        Initialize an authentication error.

        Parameters:
            detail (str): Description of the authentication failure.
        """
        super().__init__(status_code=401, detail=detail)

class AuthorizationError(AppException):
    """
    Exception for authorization (permission) failures.

    Responsibility:
        Raised when a user lacks permission to perform an action.
    When/Why:
        Use in endpoints or services to enforce access control.
    """
    def __init__(self, detail: str = "Insufficient permissions"):
        """
        Initialize an authorization error.

        Parameters:
            detail (str): Description of the authorization failure.
        """
        super().__init__(status_code=403, detail=detail)

class NotFoundError(AppException):
    """
    Exception for missing resources.

    Responsibility:
        Raised when a requested resource does not exist.
    When/Why:
        Use in endpoints/services when a DB record or file is not found.
    """
    def __init__(self, resource: str):
        """
        Initialize a not found error.

        Parameters:
            resource (str): Name of the missing resource.
        """
        super().__init__(status_code=404, detail=f"{resource} not found")

class LicenseError(AppException):
    """
    Exception for license-related errors.

    Responsibility:
        Raised when license validation or activation fails.
    When/Why:
        Use in endpoints/services that require license checks.
    """
    def __init__(self, detail: str):
        """
        Initialize a license error.

        Parameters:
            detail (str): Description of the license error.
        """
        super().__init__(status_code=403, detail=f"License error: {detail}")

class CalculationError(AppException):
    """
    Exception for calculation errors.

    Responsibility:
        Raised when a calculation fails due to invalid data or logic errors.
    When/Why:
        Use in calculation services to signal computation failures.
    """
    def __init__(self, detail: str):
        """
        Initialize a calculation error.

        Parameters:
            detail (str): Description of the calculation error.
        """
        super().__init__(status_code=500, detail=f"Calculation error: {detail}")

class ExternalServiceError(AppException):
    """
    Exception for errors from external services (APIs, SMTP, etc).

    Responsibility:
        Raised when an external dependency fails or returns an error.
    When/Why:
        Use in services that call external APIs or systems.
    """
    def __init__(self, service: str, detail: str):
        """
        Initialize an external service error.

        Parameters:
            service (str): Name of the external service.
            detail (str): Description of the error.
        """
        super().__init__(
            status_code=502,
            detail=f"External service error ({service}): {detail}"
        )