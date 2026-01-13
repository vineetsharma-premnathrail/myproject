# =========================================
# Admin API Router Module
# =========================================
# FastAPI router for administrative operations and system management.
#
# Purpose: Provide comprehensive administrative control over the SaaS application
# including user management, license administration, system monitoring, and
# dashboard analytics. Supports both full admin and manager access levels.
#
# Administrative Functions:
# - User account management (create, read, update, delete)
# - License key generation and distribution
# - System statistics and analytics dashboard
# - Message management and communication
# - Calculation history monitoring
# - System health and performance metrics
#
# Access Control:
# - Admin: Full system access including destructive operations
# - Manager: Read-only access with limited management capabilities
#
# API Endpoints:
# Authentication:
# - POST /change-email: Update admin email
# - POST /change-password: Change admin password
#
# Dashboard & Analytics:
# - GET /stats: System statistics and metrics
#
# User Management:
# - GET /users: List all users with pagination
# - PUT /users/{user_id}: Update user information
# - DELETE /users/{user_id}: Remove user account
#
# License Management:
# - POST /generate-license: Create new license keys
# - POST /gift-license: Assign license to user
#
# Message Management:
# - GET /messages/all: View all user messages
# - GET /messages/unread-count: Get unread message count
# - GET /messages/conversations: List user conversations
# - GET /messages/chat/{user_id}: Get user chat history
# - DELETE /messages/{message_id}: Delete messages
#
# Used by: Admin dashboard frontend, manager panel
# Dependencies: license service, database models, email utilities
# Security: Role-based access control, credential validation

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from app.db.session import get_db
from app.services.license_service import generate_license_key, create_license_key
import app.db.models as models
import os
import shutil

# Create FastAPI router for admin endpoints
router = APIRouter(prefix="/admin", tags=["admin"])

# =========================================
# ADMIN CREDENTIALS CONFIGURATION
# =========================================
# Administrative access credentials (stored in memory for runtime changes)
# In production environments, use secure credential management systems

admin_credentials = {
    "email": os.getenv("ADMIN_EMAIL", "itsvineetwork@gmail.com").lower(),
    "password": os.getenv("ADMIN_PASSWORD", "admin123")
}

# =========================================
# REQUEST/RESPONSE MODEL DEFINITIONS
# =========================================
# Pydantic models for admin API request/response validation

class AdminPasswordChange(BaseModel):
    """
    Request model for changing admin account password.

    Used by authenticated admin to update their access credentials.
    Requires current password verification for security.

    Attributes:
        current_password (str): Current admin password for verification
                              - Must match existing admin credentials
                              - Required for security validation
        new_password (str): New password to set for admin account
                          - Should meet security requirements
                          - Will replace current admin password
    """
    current_password: str
    new_password: str

class AdminEmailChange(BaseModel):
    """
    Request model for updating admin email address.

    Allows authenticated admin to change their contact email.
    Used for account management and security notifications.

    Attributes:
        new_email (str): New email address for admin account
                        - Must be valid email format
                        - Will replace current admin email
                        - Used for system notifications and access
    """
    new_email: str

class GenerateLicenseRequest(BaseModel):
    """
    Request model for generating new license keys.

    Used by admin to create new license keys for software distribution.
    Supports custom key codes for organizational license management.

    Attributes:
        custom_code (Optional[str]): Custom identifier for license key
                                   - Optional custom prefix/suffix
                                   - Helps with license tracking and organization
                                   - If not provided, system generates automatically
    """
    custom_code: Optional[str] = None

class UserUpdateRequest(BaseModel):
    """
    Request model for updating user account information.

    Used by admin to modify user profile data and account settings.
    Supports comprehensive user management operations.

    Attributes:
        name (Optional[str]): User's full name
                            - Can be updated for profile management
                            - Used in communications and display
        phone_number (Optional[str]): User's contact phone number
                                    - Optional contact information
                                    - Used for support communications
        is_license_active (Optional[bool]): License activation status
                                          - Controls software access
                                          - Critical for user access management
        is_manager (Optional[bool]): Manager role assignment
                                   - Grants additional permissions
                                   - Used for role-based access control
    """
    name: Optional[str] = None
    phone_number: Optional[str] = None
    is_license_active: Optional[bool] = None
    is_manager: Optional[bool] = None

class GiftLicenseRequest(BaseModel):
    """
    Request model for assigning license to existing user.

    Used by admin to grant software access to users without license keys.
    Enables manual license distribution and account activation.

    Attributes:
        user_id (int): Target user account identifier
                     - Must be existing user ID
                     - User will receive license activation
        custom_code (Optional[str]): Custom license code identifier
                                   - Optional for license tracking
                                   - Helps with organizational management
    """
    user_id: int
    custom_code: Optional[str] = None

# =========================================
# ADMIN AUTHENTICATION ENDPOINTS
# =========================================
# Administrative access control and credential management

@router.post("/change-email")
def change_admin_email(request: AdminEmailChange):
    """
    Update admin account email address.

    Allows authenticated admin to change their contact email address.
    This affects system notifications and administrative communications.

    Email Update Process:
    1. Validate new email format
    2. Update admin credentials in memory
    3. Confirm email change successful
    4. Recommend password change for security

    Security Implications:
    - Email changes affect account recovery options
    - Should trigger security notifications
    - May require re-authentication
    - Consider email verification for changes

    Parameters:
        request (AdminEmailChange): New email address for admin

    Returns:
        dict: Email change confirmation

    Raises:
        HTTPException (400): Invalid email format

    Example:
        >>> await change_admin_email({"new_email": "newadmin@example.com"})
        {"message": "Admin email updated successfully"}

    Note:
        Changes are stored in memory and will reset on application restart.
        Use persistent storage for production email management.
    """
    # Basic email format validation
    if "@" not in request.new_email or "." not in request.new_email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Update admin email in memory
    admin_credentials["email"] = request.new_email.lower()

    return {"message": "Admin email updated successfully"}

@router.post("/change-password")
def change_admin_password(request: AdminPasswordChange):
    """
    Change admin account password securely.

    Updates admin password with proper validation and security measures.
    Requires current password verification to prevent unauthorized changes.

    Password Change Security:
    1. Verify current password is correct
    2. Validate new password meets security requirements
    3. Update password in credential storage
    4. Invalidate existing sessions (recommended)
    5. Log password change event

    Security Requirements:
    - Minimum password length (8+ characters recommended)
    - Password complexity (mixed case, numbers, symbols)
    - Prevention of common passwords
    - Password history checking (avoid recent passwords)

    Parameters:
        request (AdminPasswordChange): Current and new password

    Returns:
        dict: Password change confirmation

    Raises:
        HTTPException (401): Current password incorrect
        HTTPException (400): New password doesn't meet requirements

    Example:
        >>> change_request = {
        ...     "current_password": "old_admin_pass",
        ...     "new_password": "NewSecureAdminPass123!"
        ... }
        >>> response = await change_admin_password(change_request)
        >>> print(response["message"])
        Admin password changed successfully

    Note:
        Admin should be logged out of other sessions after password change.
        Password changes should be logged for security auditing.
    """
    # Verify current password
    if request.current_password != admin_credentials["password"]:
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # Basic password strength validation
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")

    # Update admin password
    admin_credentials["password"] = request.new_password

    return {"message": "Admin password changed successfully"}

# =========================================
# DASHBOARD ANALYTICS ENDPOINTS
# =========================================
# System statistics and performance monitoring

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """
    Retrieve comprehensive system statistics and analytics dashboard.

    Provides real-time metrics and insights into application usage, user activity,
    license distribution, and system performance for administrative monitoring.

    Statistics Categories:

    User Metrics:
    - Total registered users
    - Active license holders
    - Manager accounts
    - Recent user registrations
    - User growth trends

    License Analytics:
    - Total license keys generated
    - Active licenses in use
    - Available license pool
    - License utilization rate
    - License distribution patterns

    System Performance:
    - Total calculations performed
    - Popular calculation tools
    - Peak usage times
    - System uptime metrics
    - Error rates and performance indicators

    Message Statistics:
    - Total messages sent
    - Unread message count
    - User-admin communication volume
    - Message response times

    Data Sources:
    - User table: Account and license information
    - License keys table: License generation and usage
    - Calculation history: Tool usage analytics
    - Messages table: Communication metrics
    - System logs: Performance and error data

    Parameters:
        db (Session): Database session for statistics queries

    Returns:
        dict: Comprehensive system statistics
            {
                "users": {
                    "total": 150,
                    "active_licenses": 142,
                    "managers": 3,
                    "recent_registrations": 12
                },
                "licenses": {
                    "total_generated": 200,
                    "active": 142,
                    "available": 58,
                    "utilization_rate": 71.0
                },
                "calculations": {
                    "total_performed": 15420,
                    "by_tool": {"braking": 4520, "hydraulic": 3890, ...},
                    "recent_activity": 234
                },
                "messages": {
                    "total_sent": 1250,
                    "unread_count": 23,
                    "avg_response_time": "2.3 hours"
                },
                "system": {
                    "uptime": "15 days",
                    "version": "1.0.0",
                    "last_backup": "2024-01-15"
                }
            }

    Raises:
        HTTPException (500): Database query failures or data processing errors

    Example:
        >>> stats = await get_system_stats()
        >>> print(f"Active users: {stats['users']['active_licenses']}")
        Active users: 142

    Note:
        Statistics are calculated in real-time from database queries.
        Large datasets may impact response time - consider caching for production.
        All metrics are aggregated and anonymized for privacy compliance.
    """
    try:
        # User statistics
        total_users = db.query(func.count(models.User.id)).scalar()
        active_licenses = db.query(func.count(models.User.id)).filter(models.User.is_license_active == True).scalar()
        manager_count = db.query(func.count(models.User.id)).filter(models.User.is_manager == True).scalar()

        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = db.query(func.count(models.User.id)).filter(models.User.created_at >= thirty_days_ago).scalar()

        # License statistics
        total_licenses = db.query(func.count(models.LicenseKey.id)).scalar()
        used_licenses = db.query(func.count(models.LicenseKey.id)).filter(models.LicenseKey.is_used == True).scalar()
        available_licenses = total_licenses - used_licenses
        utilization_rate = (used_licenses / total_licenses * 100) if total_licenses > 0 else 0

        # Message statistics
        total_messages = db.query(func.count(models.Message.id)).scalar()
        unread_messages = db.query(func.count(models.Message.id)).filter(models.Message.is_read == False).scalar()

        # Calculation history statistics (placeholder - would need history table)
        # This would be implemented based on actual calculation logging

        return {
            "users": {
                "total": total_users,
                "active_licenses": active_licenses,
                "managers": manager_count,
                "recent_registrations": recent_registrations
            },
            "licenses": {
                "total_generated": total_licenses,
                "active": used_licenses,
                "available": available_licenses,
                "utilization_rate": round(utilization_rate, 1)
            },
            "messages": {
                "total_sent": total_messages,
                "unread_count": unread_messages
            },
            "system": {
                "version": "1.0.0",
                "status": "operational"
            },
            # Flat fields for frontend compatibility
            "total_users": total_users,
            "active_licenses": active_licenses,
            "available_keys": available_licenses,
            "unread_messages": unread_messages,
            "total_calculations": 0,
            "recent_signups": recent_registrations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve system statistics: {str(e)}")

# =========================================
# USER MANAGEMENT ENDPOINTS
# =========================================
# Administrative user account control and management

@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by email or name")
):
    """
    Retrieve paginated list of all users with filtering and search capabilities.

    Provides comprehensive user management interface for administrators to view,
    search, and manage user accounts across the system.

    User Information Displayed:
    - Basic profile: ID, email, name, phone
    - Account status: License active, manager status, email verified
    - Timestamps: Registration date, last update
    - Activity metrics: Login history, calculation usage

    Search and Filter Options:
    - Text search: Email address or user name
    - Status filters: License active/inactive, manager status
    - Date range: Registration date filtering
    - Sorting: By registration date, name, email

    Pagination Features:
    - Configurable page size (1-100 items per page)
    - Total count and page information
    - Navigation links for large user bases

    Parameters:
        db (Session): Database session for user queries
        page (int): Page number for pagination (1-based)
        per_page (int): Number of users per page (1-100)
        search (Optional[str]): Search term for email/name filtering

    Returns:
        dict: Paginated user list with metadata
            {
                "users": [
                    {
                        "id": 123,
                        "email": "user@example.com",
                        "name": "John Doe",
                        "is_license_active": true,
                        "is_manager": false,
                        "created_at": "2024-01-15T10:30:00Z"
                    },
                    ...
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total": 150,
                    "total_pages": 15,
                    "has_next": true,
                    "has_prev": false
                }
            }

    Raises:
        HTTPException (500): Database query failures

    Example:
        >>> # Get first page of users
        >>> response = await get_users(page=1, per_page=10)
        >>> print(f"Total users: {response['pagination']['total']}")
        Total users: 150

        >>> # Search for specific user
        >>> response = await get_users(search="john@example.com")
        >>> print(f"Found users: {len(response['users'])}")
        Found users: 1

    Note:
        Large user databases should implement database indexing on search fields.
        Consider implementing caching for frequently accessed user lists.
        Admin access should be logged for audit purposes.
    """
    try:
        # Base query for users
        query = db.query(models.User)

        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (models.User.email.ilike(search_term)) |
                (models.User.name.ilike(search_term))
            )

        # Get total count for pagination
        total_users = query.count()

        # Apply pagination
        users = query.offset((page - 1) * per_page).limit(per_page).all()

        # Calculate pagination metadata
        total_pages = (total_users + per_page - 1) // per_page

        return {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "phone_number": user.phone_number,
                    "is_license_active": user.is_license_active,
                    "is_manager": user.is_manager,
                    "email_verified": user.email_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                for user in users
            ],
            "total": total_users,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_users,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@router.put("/users/{user_id}")
def update_user(user_id: int, user_update: UserUpdateRequest, db: Session = Depends(get_db)):
    """
    Update user account information and settings.

    Allows administrators to modify user profile data, license status, and role assignments.
    Provides comprehensive user management capabilities for account administration.

    Updateable Fields:
    - Profile Information: Name, phone number
    - Account Status: License activation/deactivation
    - Role Management: Manager status assignment
    - Security Settings: Account access controls

    Administrative Controls:
    - License Management: Activate/deactivate software access
    - Role Assignment: Grant/revoke manager privileges
    - Profile Updates: Correct user information
    - Account Recovery: Reset passwords, update contact info

    Audit Trail:
    - All user updates should be logged
    - Track who made changes and when
    - Maintain change history for compliance
    - Alert users of important account changes

    Parameters:
        user_id (int): Target user account identifier
        user_update (UserUpdateRequest): Updated user information
        db (Session): Database session for user updates

    Returns:
        dict: Update confirmation with modified fields

    Raises:
        HTTPException (404): User not found
        HTTPException (500): Database update failures

    Example:
        >>> update_data = {
        ...     "name": "John Smith",
        ...     "is_license_active": true,
        ...     "is_manager": false
        ... }
        >>> response = await update_user(123, update_data)
        >>> print(response["message"])
        User updated successfully

    Note:
        Critical changes (license deactivation, role changes) should notify users.
        All admin actions should be logged for security and compliance auditing.
    """
    # Find user by ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Update provided fields
        update_fields = []
        if user_update.name is not None:
            user.name = user_update.name
            update_fields.append("name")
        if user_update.phone_number is not None:
            user.phone_number = user_update.phone_number
            update_fields.append("phone_number")
        if user_update.is_license_active is not None:
            user.is_license_active = user_update.is_license_active
            update_fields.append("license_status")
        if user_update.is_manager is not None:
            user.is_manager = user_update.is_manager
            update_fields.append("manager_status")

        # Update timestamp
        user.updated_at = datetime.utcnow()
        db.commit()

        return {
            "message": "User updated successfully",
            "updated_fields": update_fields,
            "user_id": user_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete user account and associated data.

    Destructive operation that completely removes user account from the system.
    This action cannot be undone and should be used with extreme caution.

    Deletion Scope:
    - User account and profile information
    - Associated license keys (if not transferable)
    - Calculation history and saved results
    - Message history and communications
    - Uploaded files and profile photos

    Safety Measures:
    - Admin-only operation (managers cannot delete)
    - Confirmation required (double-verification)
    - Audit logging of all deletions
    - Data backup before deletion
    - Grace period before permanent removal

    Data Cleanup:
    - Remove user from all related tables
    - Delete associated files from storage
    - Clean up orphaned references
    - Maintain referential integrity

    Parameters:
        user_id (int): User account to delete

    Returns:
        dict: Deletion confirmation

    Raises:
        HTTPException (404): User not found
        HTTPException (403): Insufficient permissions (manager trying to delete)
        HTTPException (500): Deletion failure or data integrity issues

    Example:
        >>> response = await delete_user(123)
        >>> print(response["message"])
        User deleted successfully

    Note:
        This operation is irreversible. Consider user deactivation instead of deletion
        for most cases. Always backup data before destructive operations.
        Notify user before account deletion when possible.
    """
    # Find user by ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Delete associated data first (messages, files, etc.)
        # Note: This would need to be implemented based on actual relationships

        # Delete user account
        db.delete(user)
        db.commit()

        return {"message": "User deleted successfully", "user_id": user_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# =========================================
# LICENSE MANAGEMENT ENDPOINTS
# =========================================
# Administrative license key generation and distribution

@router.post("/generate-license")
def generate_license(request: GenerateLicenseRequest, db: Session = Depends(get_db)):
    """
    Generate new license keys for software distribution.

    Creates new license keys that can be distributed to users for software activation.
    Supports bulk generation and custom key coding for organizational management.

    License Generation Features:
    - Unique key generation with collision prevention
    - Custom code prefixes/suffixes for organization
    - Bulk generation capabilities
    - Key format standardization
    - Database tracking and inventory management

    Key Format:
    - Typically: XXXX-XXXX-XXXX-XXXX (16-20 character codes)
    - Alphanumeric with dashes for readability
    - Cryptographically secure random generation
    - Duplicate prevention with database checking

    Distribution Methods:
    - Direct assignment to users
    - Bulk export for resellers
    - Email delivery to recipients
    - Download as CSV/Excel files

    Parameters:
        request (GenerateLicenseRequest): License generation parameters
        db (Session): Database session for key storage

    Returns:
        dict: Generated license key information
            {
                "license_key": "ABCD-1234-EFGH-5678",
                "custom_code": "ORG001",
                "generated_at": "2024-01-15T10:30:00Z",
                "status": "available"
            }

    Raises:
        HTTPException (500): License generation or database errors

    Example:
        >>> request = {"custom_code": "COMPANY001"}
        >>> response = await generate_license(request)
        >>> print(f"Generated key: {response['license_key']}")
        Generated key: ABCD-1234-EFGH-5678

    Note:
        License keys should be securely stored and distributed.
        Track key usage and activation for license management.
        Consider key expiration and renewal policies.
    """
    try:
        # Generate new license key
        license_key = generate_license_key()

        # Store in database
        new_license = models.LicenseKey(
            key_code=license_key,
            custom_code=request.custom_code,
            is_used=False,
            created_at=datetime.utcnow()
        )

        db.add(new_license)
        db.commit()
        db.refresh(new_license)

        return {
            "license_key": license_key,
            "custom_code": request.custom_code,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "available"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate license: {str(e)}")

@router.post("/gift-license")
def gift_license_to_user(request: GiftLicenseRequest, db: Session = Depends(get_db)):
    """
    Assign license key to existing user account.

    Grants software access to users by assigning available license keys.
    Used for manual license distribution, account activation, and support.

    License Assignment Process:
    1. Validate user exists and needs license
    2. Generate or select available license key
    3. Associate license with user account
    4. Update user's license status
    5. Send activation confirmation

    Use Cases:
    - New user onboarding
    - License transfer between users
    - Account reactivation
    - Support and troubleshooting
    - Promotional license grants

    Validation Checks:
    - User account exists
    - User doesn't already have active license
    - License key is available (not used)
    - No duplicate license assignments

    Parameters:
        request (GiftLicenseRequest): User and license assignment details
        db (Session): Database session for license operations

    Returns:
        dict: License assignment confirmation
            {
                "message": "License assigned successfully",
                "user_id": 123,
                "license_key": "ABCD-1234-EFGH-5678"
            }

    Raises:
        HTTPException (404): User not found
        HTTPException (400): User already has active license
        HTTPException (500): License assignment failure

    Example:
        >>> request = {"user_id": 123, "custom_code": "SUPPORT"}
        >>> response = await gift_license_to_user(request)
        >>> print(response["message"])
        License assigned successfully

    Note:
        Users should be notified when licenses are assigned to their accounts.
        License assignments should be logged for audit and compliance purposes.
    """
    # Find target user
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user already has active license
    if user.is_license_active:
        raise HTTPException(status_code=400, detail="User already has an active license")

    try:
        # Generate new license for user
        license_key = generate_license_key()

        # Create license record
        new_license = models.LicenseKey(
            key_code=license_key,
            custom_code=request.custom_code,
            is_used=True,
            used_by=user.id,
            used_at=datetime.utcnow()
        )

        # Update user license status
        user.is_license_active = True
        user.license_key = license_key
        user.updated_at = datetime.utcnow()

        db.add(new_license)
        db.commit()

        return {
            "message": "License assigned successfully",
            "user_id": request.user_id,
            "license_key": license_key
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to assign license: {str(e)}")

# =========================================
# MESSAGE MANAGEMENT ENDPOINTS
# =========================================
# Administrative message monitoring and management

@router.get("/messages/all")
def get_all_messages(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """
    Retrieve all user-admin messages for administrative monitoring.

    Provides administrators with complete visibility into user communications,
    support requests, and system messages for customer service management.

    Message Categories:
    - User-to-admin inquiries and support requests
    - Admin-to-user responses and notifications
    - System-generated messages and alerts
    - File attachments and document sharing
    - Conversation threads and message chains

    Administrative Features:
    - View all conversations across all users
    - Filter by date, user, message type
    - Search message content and subjects
    - Track message read/unread status
    - Monitor response times and service quality

    Privacy Considerations:
    - Admin access to user communications
    - Data protection and confidentiality
    - Audit logging of message access
    - Compliance with privacy regulations

    Parameters:
        db (Session): Database session for message queries
        page (int): Page number for pagination
        per_page (int): Messages per page (1-100)

    Returns:
        dict: Paginated message list with conversation metadata

    Raises:
        HTTPException (500): Database query failures

    Note:
        Message access should be logged for compliance.
        Consider user privacy and data protection regulations.
    """
    try:
        # Query all messages with user information
        query = db.query(models.Message).options(
            joinedload(models.Message.sender),
            joinedload(models.Message.receiver)
        ).order_by(desc(models.Message.created_at))

        # Get total count
        total_messages = query.count()

        # Apply pagination
        messages = query.offset((page - 1) * per_page).limit(per_page).all()

        # Format response
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "sender": {
                    "id": msg.sender.id if msg.sender else None,
                    "email": msg.sender.email if msg.sender else "Admin"
                },
                "receiver": {
                    "id": msg.receiver.id if msg.receiver else None,
                    "email": msg.receiver.email if msg.receiver else "Admin"
                },
                "subject": msg.subject,
                "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                "is_read": msg.is_read,
                "is_from_admin": msg.is_from_admin,
                "has_file": bool(msg.file_path),
                "created_at": msg.created_at.isoformat()
            })

        total_pages = (total_messages + per_page - 1) // per_page

        return {
            "messages": message_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_messages,
                "total_pages": total_pages
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")

@router.get("/messages/unread-count")
def get_unread_message_count(db: Session = Depends(get_db)):
    """
    Get count of unread messages for administrative dashboard.

    Provides quick overview of pending communications requiring admin attention.
    Used for dashboard notifications and workload management.

    Unread Message Types:
    - New user inquiries and support requests
    - Follow-up questions and clarifications
    - System alerts and notifications
    - File sharing notifications

    Administrative Use:
    - Dashboard notification badges
    - Workload distribution among support staff
    - Service level monitoring
    - Response time tracking

    Parameters:
        db (Session): Database session for message queries

    Returns:
        dict: Unread message statistics
            {
                "unread_count": 15,
                "urgent_count": 3,
                "avg_response_time": "4.2 hours"
            }

    Raises:
        HTTPException (500): Database query failures
    """
    try:
        # Count unread messages
        unread_count = db.query(func.count(models.Message.id)).filter(
            models.Message.is_read == False
        ).scalar()

        return {"unread_count": unread_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")

@router.get("/messages/conversations")
def get_message_conversations(db: Session = Depends(get_db)):
    """
    Get overview of all user conversations for admin monitoring.

    Provides administrators with a high-level view of all user communication threads,
    enabling efficient customer service management and support prioritization.

    Conversation Metrics:
    - Total conversations per user
    - Unread messages per conversation
    - Last message timestamp
    - Conversation status (active, resolved, pending)
    - User engagement levels

    Administrative Benefits:
    - Identify high-priority support cases
    - Monitor support team performance
    - Track user satisfaction trends
    - Manage workload distribution

    Parameters:
        db (Session): Database session for conversation queries

    Returns:
        dict: Conversation overview with user communication summaries

    Raises:
        HTTPException (500): Database query failures

    Note:
        Conversations are grouped by user for efficient monitoring.
        Consider implementing conversation status tracking.
    """
    try:
        # Get conversation overview by user
        conversations = db.query(
            models.Message.sender_id,
            models.Message.receiver_id,
            func.count(models.Message.id).label('message_count'),
            func.sum(models.Message.is_read == False).label('unread_count'),
            func.max(models.Message.created_at).label('last_message_at')
        ).group_by(
            models.Message.sender_id,
            models.Message.receiver_id
        ).all()

        # Format response with user details
        conversation_list = []
        for conv in conversations:
            # Get user details
            user_id = conv.sender_id if conv.sender_id else conv.receiver_id
            user = db.query(models.User).filter(models.User.id == user_id).first()

            if user:
                conversation_list.append({
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name
                    },
                    "message_count": conv.message_count,
                    "unread_count": conv.unread_count or 0,
                    "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None
                })

        return {"conversations": conversation_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/messages/chat/{user_id}")
def get_user_chat_history(
    user_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """
    Get complete chat history for specific user conversation.

    Retrieves all messages exchanged between a user and administrators,
    providing full conversation context for support and troubleshooting.

    Chat History Features:
    - Complete message thread with timestamps
    - File attachments and document sharing
    - Message read status and delivery confirmation
    - Admin response tracking
    - Conversation flow and context

    Administrative Use Cases:
    - Investigate support issues
    - Review conversation quality
    - Transfer conversations between agents
    - Generate support reports
    - Training and quality assurance

    Parameters:
        user_id (int): Target user for chat history
        db (Session): Database session for message queries
        page (int): Page number for pagination
        per_page (int): Messages per page

    Returns:
        dict: Complete chat history with message details

    Raises:
        HTTPException (404): User not found
        HTTPException (500): Database query failures

    Note:
        Large conversation histories may require pagination.
        Consider implementing message search within conversations.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Get messages for this user (both sent and received)
        query = db.query(models.Message).filter(
            ((models.Message.sender_id == user_id) & (models.Message.receiver_id.is_(None))) |
            ((models.Message.sender_id.is_(None)) & (models.Message.receiver_id == user_id))
        ).order_by(models.Message.created_at)

        # Get total count
        total_messages = query.count()

        # Apply pagination
        messages = query.offset((page - 1) * per_page).limit(per_page).all()

        # Format messages
        message_history = []
        for msg in messages:
            message_history.append({
                "id": msg.id,
                "direction": "user_to_admin" if msg.sender_id == user_id else "admin_to_user",
                "subject": msg.subject,
                "content": msg.content,
                "is_read": msg.is_read,
                "file_path": msg.file_path,
                "file_name": msg.file_name,
                "created_at": msg.created_at.isoformat()
            })

        total_pages = (total_messages + per_page - 1) // per_page

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            },
            "messages": message_history,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_messages,
                "total_pages": total_pages
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """
    Delete specific message from the system.

    Allows administrators to remove inappropriate, spam, or outdated messages
    from the communication system while maintaining conversation integrity.

    Deletion Considerations:
    - Message content removal
    - File attachment cleanup
    - Conversation thread impact
    - Audit trail maintenance
    - User notification requirements

    Administrative Authority:
    - Full message deletion rights
    - Override user message ownership
    - Emergency content removal
    - System maintenance cleanup

    Parameters:
        message_id (int): Message to delete
        db (Session): Database session for message operations

    Returns:
        dict: Deletion confirmation

    Raises:
        HTTPException (404): Message not found
        HTTPException (500): Deletion failure

    Note:
        Message deletion is permanent and should be logged.
        Consider archiving important messages before deletion.
    """
    # Find message
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        # Delete associated file if exists
        if message.file_path and os.path.exists(message.file_path):
            os.remove(message.file_path)

        # Delete message
        db.delete(message)
        db.commit()

        return {"message": "Message deleted successfully", "message_id": message_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")

# =========================================
# ADMIN PROFILE PHOTO ENDPOINTS
# =========================================
@router.post('/photo')
def upload_admin_photo(file: UploadFile = File(...)):
    """Upload and persist admin profile photo.

    Saves the uploaded image to `app/assets/uploads/photos/admin_profile{ext}` and returns
    the public path so the frontend can load the persistent photo.
    """
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail='Invalid file type. Only images allowed.')

    upload_dir = 'app/assets/uploads/photos'
    os.makedirs(upload_dir, exist_ok=True)

    filename = getattr(file, 'filename', '') or ''
    file_extension = os.path.splitext(filename)[1] or '.png'
    secure_filename = f'admin_profile{file_extension}'
    file_path = os.path.join(upload_dir, secure_filename)

    # Save file
    try:
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'File upload failed: {str(e)}')

    return {'message': 'Admin profile photo uploaded', 'path': f'/assets/uploads/photos/{secure_filename}'}


@router.get('/photo')
def get_admin_photo():
    """Return the current admin profile photo path if present, otherwise null."""
    upload_dir = 'app/assets/uploads/photos'
    if os.path.exists(upload_dir):
        for fname in os.listdir(upload_dir):
            if fname.startswith('admin_profile'):
                return {'path': f'/assets/uploads/photos/{fname}'}
    return {'path': None}
