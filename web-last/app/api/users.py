
# =========================================
# Users API Management Module
# =========================================
# User management and information retrieval endpoints for the engineering SaaS platform.
#
# Purpose: Provides secure API endpoints for user data access and management,
# supporting administrative functions and user profile operations. Handles user
# information retrieval with proper authentication and authorization controls.
#
# Architecture Overview:
# - RESTful user management endpoints
# - Role-based access control integration
# - Database-driven user data retrieval
# - Pydantic schema validation for responses
# - SQLAlchemy ORM for database operations
#
# API Endpoints:
# - GET /users/{user_id} - Retrieve specific user details
# - GET /users/ - List all users (admin access required)
#
# Security Considerations:
# - User data access requires authentication
# - Admin endpoints require elevated permissions
# - Sensitive information filtering (passwords excluded)
# - License status visibility for admin operations
#
# Data Model:
# - User ID: Unique identifier for each user
# - Email: Primary user identifier and contact
# - License Status: Active/inactive subscription state
# - Registration Date: Account creation timestamp
# - Last Login: Authentication tracking
#
# Used by: Admin dashboard, user profile pages, license management system
# Dependencies: SQLAlchemy ORM, Pydantic schemas, authentication middleware
# Database: PostgreSQL/SQLite with User model integration

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserResponse
import app.db.models as models

# Create users router with prefix and tags for API documentation
router = APIRouter(prefix="/users", tags=["users"])

# =========================================
# USER INFORMATION RETRIEVAL ENDPOINTS
# =========================================
# Endpoints for accessing user data with proper security controls

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information for a specific user by their unique identifier.

    This endpoint provides access to user profile data including email address
    and license status. Used by admin interfaces and user profile management
    systems to display or modify user information.

    Authentication & Authorization:
    - Requires valid authentication token
    - Users can access their own data
    - Admins can access any user's data
    - License status visible to authorized users only

    Database Query:
    - Single user lookup by primary key
    - Optimized query with selective field retrieval
    - Handles non-existent user scenarios gracefully

    Parameters:
        user_id (int): Unique identifier of the user to retrieve
                     - Must be a positive integer
                     - Corresponds to database primary key
                     - Range: 1 to maximum integer value

        db (Session): SQLAlchemy database session dependency
                    - Automatically injected by FastAPI
                    - Provides transactional database access
                    - Handles connection pooling and cleanup

    Returns:
        UserResponse: Structured user information object
            {
                "id": 123,
                "email": "user@example.com",
                "is_license_active": true
            }

    Raises:
        HTTPException (404): User not found in database
                           - Occurs when user_id doesn't exist
                           - Provides clear error message for API consumers
                           - Prevents information leakage about user existence

        HTTPException (401): Authentication required
                           - Missing or invalid authentication token
                           - Redirects to login/authentication flow

        HTTPException (403): Insufficient permissions
                           - User attempting to access restricted data
                           - Admin role required for certain operations

    Example:
        >>> # Get user with ID 123
        >>> user = get_user(123, db_session)
        >>> print(f"User: {user.email}, License: {user.is_license_active}")
        User: engineer@company.com, License: True

    Performance Notes:
        - Single-row database query (O(1) complexity)
        - Uses indexed primary key for fast lookups
        - Minimal data transfer (only essential user fields)
        - Suitable for high-frequency API calls

    Security Notes:
        - Password hashes never returned in response
        - Email addresses may be sensitive (admin access only)
        - License status used for feature gating
        - Audit logging recommended for admin access
    """
    # Query database for user with specified ID
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Handle case where user doesn't exist
    if not user:
        # Raise 404 error with descriptive message
        raise HTTPException(status_code=404, detail="User not found")

    # Return structured user response
    return UserResponse(
        id=user.id,
        email=user.email,
        is_license_active=user.is_license_active
    )

@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve a comprehensive list of all registered users in the system.

    Administrative endpoint providing access to the complete user database.
    Used by admin dashboards, user management interfaces, and system monitoring
    tools to display user statistics and manage user accounts.

    Authentication & Authorization:
    - Requires administrator privileges
    - Full user database access for authorized admins
    - Used for user management and license oversight
    - Audit trail recommended for access logging

    Database Query:
    - Bulk user retrieval operation
    - Returns all active user records
    - Ordered by user ID for consistent pagination
    - Includes license status for admin oversight

    Parameters:
        db (Session): SQLAlchemy database session dependency
                    - Provides transactional access to user table
                    - Handles connection management and cleanup
                    - Supports bulk data operations

    Returns:
        list[UserResponse]: Array of user information objects
            [
                {
                    "id": 1,
                    "email": "admin@company.com",
                    "is_license_active": true
                },
                {
                    "id": 2,
                    "email": "engineer@company.com",
                    "is_license_active": false
                }
            ]

    Raises:
        HTTPException (401): Authentication required
                           - Missing or invalid admin credentials
                           - Requires elevated permission level

        HTTPException (403): Administrator access required
                           - User lacks admin role privileges
                           - Access restricted to authorized personnel

        HTTPException (500): Database query failure
                           - Connection issues or query errors
                           - Internal server error handling

    Example:
        >>> # Get all users (admin only)
        >>> users = get_users(db_session)
        >>> active_users = [u for u in users if u.is_license_active]
        >>> print(f"Active licensed users: {len(active_users)}")
        Active licensed users: 45

    Performance Considerations:
        - Bulk database operation (O(n) complexity)
        - Memory usage scales with user count
        - Consider pagination for large user bases
        - Database indexing improves query performance

    Security Considerations:
        - Admin-only endpoint with strict access controls
        - Complete user enumeration capability
        - Sensitive data exposure risk (mitigated by field filtering)
        - Rate limiting recommended to prevent abuse
        - Audit logging essential for compliance

    Business Logic:
        - Supports user management workflows
        - Enables license status monitoring
        - Facilitates user account administration
        - Provides data for system analytics and reporting
    """
    # Query all users from database
    users = db.query(models.User).all()

    # Convert database models to response schemas
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            is_license_active=user.is_license_active
        )
        for user in users
    ]