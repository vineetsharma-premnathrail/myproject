
"""
Permissions and Authorization Module
-----------------------------------
Purpose:
    Provides role-based access control (RBAC) and permission checking utilities for the backend.
    Used to enforce security and restrict access to sensitive endpoints and features.
Layer:
    Backend / Security / Authorization
"""

from typing import List
from fastapi import HTTPException, status

class Permission:
    """
    Permission constants for all business actions.

    Responsibility:
        Defines all possible permissions that can be assigned to roles.
    When/Why:
        Used to check if a user can perform a specific action.
    """
    CALCULATE_BRAKING = "calculate:braking"
    CALCULATE_QMAX = "calculate:qmax"
    CALCULATE_HYDRAULIC = "calculate:hydraulic"
    CALCULATE_LOAD_DISTRIBUTION = "calculate:load_distribution"
    CALCULATE_TRACTIVE_EFFORT = "calculate:tractive_effort"
    CALCULATE_VEHICLE_PERFORMANCE = "calculate:vehicle_performance"
    DOWNLOAD_REPORTS = "download:reports"
    MANAGE_USERS = "manage:users"
    MANAGE_LICENSES = "manage:licenses"

class Role:
    """
    Role constants for user types.

    Responsibility:
        Defines all user roles in the system.
    When/Why:
        Used to assign and check permissions for users.
    """
    USER = "user"
    ADMIN = "admin"
    PREMIUM_USER = "premium_user"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    Role.USER: [
        Permission.CALCULATE_BRAKING,
        Permission.CALCULATE_QMAX,
        Permission.CALCULATE_HYDRAULIC,
        Permission.DOWNLOAD_REPORTS,
    ],
    Role.PREMIUM_USER: [
        Permission.CALCULATE_BRAKING,
        Permission.CALCULATE_QMAX,
        Permission.CALCULATE_HYDRAULIC,
        Permission.CALCULATE_LOAD_DISTRIBUTION,
        Permission.CALCULATE_TRACTIVE_EFFORT,
        Permission.CALCULATE_VEHICLE_PERFORMANCE,
        Permission.DOWNLOAD_REPORTS,
    ],
    Role.ADMIN: [
        Permission.CALCULATE_BRAKING,
        Permission.CALCULATE_QMAX,
        Permission.CALCULATE_HYDRAULIC,
        Permission.CALCULATE_LOAD_DISTRIBUTION,
        Permission.CALCULATE_TRACTIVE_EFFORT,
        Permission.CALCULATE_VEHICLE_PERFORMANCE,
        Permission.DOWNLOAD_REPORTS,
        Permission.MANAGE_USERS,
        Permission.MANAGE_LICENSES,
    ],
}

def check_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a user role has the required permission.

    Parameters:
        user_role (str): The user's role (e.g., 'user', 'admin')
        required_permission (str): The permission to check

    Returns:
        bool: True if the role has the permission, False otherwise
    """
    if user_role not in ROLE_PERMISSIONS:
        return False
    return required_permission in ROLE_PERMISSIONS[user_role]

def require_permission(required_permission: str):
    """
    Decorator factory to enforce permission checks on functions.

    Parameters:
        required_permission (str): The permission required to access the function

    Returns:
        function: Decorator that checks permission before calling the function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # In a real implementation, get user role from JWT token or session
            # For demonstration, assume basic user role
            user_role = Role.USER
            if not check_permission(user_role, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator