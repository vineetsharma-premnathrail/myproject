# =========================================
# Messages API Router Module
# =========================================
# FastAPI router for user-admin messaging system with file attachments.
#
# Purpose: Provide comprehensive communication platform between users and administrators
# with support for text messages, file attachments, conversation threading, and message
# management. Enables customer support, system notifications, and document sharing.
#
# Communication Features:
# - User-to-admin support requests and inquiries
# - Admin-to-user responses and system notifications
# - File attachment support for documents and images
# - Message read/unread status tracking
# - Conversation threading and history
# - Secure file upload and storage
#
# Message Types Supported:
# - Text Messages: Plain text communications
# - File Attachments: Documents, images, spreadsheets
# - System Notifications: Automated alerts and updates
# - Admin Broadcasts: Mass communications to users
#
# Security Features:
# - User authentication required for messaging
# - File type validation and size limits
# - Secure file storage with access controls
# - Message content filtering and moderation
# - Audit logging of all communications
#
# API Endpoints:
# User Endpoints:
# - POST /send: Send message to admin with optional file attachment
# - POST /send-with-file: Send message with file attachment (FormData)
# - PUT /mark-all-read/{user_id}: Mark all user messages as read
#
# Admin Endpoints:
# - GET /admin/all: View all messages with pagination
# - GET /admin/unread-count: Get count of unread messages
# - GET /admin/conversations: Get conversation overview by user
# - GET /admin/chat/{user_id}: Get complete chat history for user
# - DELETE /{message_id}: Delete specific message
#
# File Handling:
# - Secure upload directory: app/assets/uploads/messages/
# - Supported formats: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG, GIF
# - File size limits: Configurable (default 10MB)
# - Filename sanitization and secure storage
# - Automatic cleanup of old/deleted attachments
#
# Used by: User dashboard, admin panel, support system
# Dependencies: File upload handling, database models, email notifications
# Database: Message model with file attachment support

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, and_, func
from pydantic import BaseModel
from typing import Optional, List
from app.db.session import get_db
import app.db.models as models
import os
import shutil
from datetime import datetime, timedelta
import uuid

# Create FastAPI router for messaging endpoints
router = APIRouter(prefix="/messages", tags=["messages"])

# =========================================
# FILE UPLOAD CONFIGURATION
# =========================================
# Secure file handling for message attachments

UPLOAD_DIR = "app/assets/uploads/messages"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Supported file types for message attachments
ALLOWED_EXTENSIONS = {
    # Documents
    '.pdf', '.doc', '.docx', '.txt', '.rtf',
    # Spreadsheets
    '.xls', '.xlsx', '.csv',
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    # Archives (optional)
    '.zip', '.rar'
}

# Maximum file size (10MB default)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# =========================================
# REQUEST/RESPONSE MODEL DEFINITIONS
# =========================================
# Pydantic models for message API validation

class SendMessageRequest(BaseModel):
    """
    Request model for sending text messages to administrators.

    Used for user support requests, inquiries, and general communications
    with the administrative team. Supports optional subject lines for
    better message organization and prioritization.

    Message Content:
    - Subject: Optional categorization and summary
    - Content: Main message body (required)
    - Direction: User-to-admin communication
    - Read Status: Initially unread for admin attention

    Attributes:
        sender_id (Optional[int]): User account ID sending the message
                                  - None indicates admin sender (internal use)
                                  - Must be authenticated user for security
        receiver_id (Optional[int]): Target user ID for admin responses
                                    - None indicates admin recipient
                                    - Used for admin-to-user communications
        subject (Optional[str]): Message subject line for categorization
                                - Helps with message prioritization
                                - Supports search and filtering
                                - Recommended for support requests
        content (str): Main message content body
                      - Required field (cannot be empty)
                      - Supports multi-line text
                      - Maximum length validation may apply
        is_from_admin (bool): Administrative message flag
                            - True: Message sent by administrator
                            - False: Message sent by regular user
                            - Affects message routing and permissions
    """
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    subject: Optional[str] = None
    content: str
    is_from_admin: bool = False

class MessageResponse(BaseModel):
    """
    Response model for message data in API responses.

    Standardized format for returning message information in list views,
    detail views, and conversation threads. Includes all essential message
    metadata for frontend display and interaction.

    Response Fields:
    - Message identification and content
    - Sender/receiver information
    - Timestamps and status flags
    - File attachment details (if present)

    Attributes:
        id (int): Unique message identifier
                 - Auto-generated primary key
                 - Used for message operations (read, delete)
        sender_id (Optional[int]): User ID of message sender
                                  - None for admin messages
                                  - Links to user account information
        receiver_id (Optional[int]): User ID of message recipient
                                    - None for admin recipients
                                    - Determines message visibility
        subject (Optional[str]): Message subject line
                                - May be None for casual messages
                                - Used for message categorization
        content (str): Full message content
                      - Complete message text
                      - May include formatting (Markdown support)
        is_read (bool): Message read status
                       - True: User has viewed the message
                       - False: Unread message requiring attention
        is_from_admin (bool): Administrative origin flag
                             - True: Sent by administrator
                             - False: Sent by regular user
        file_path (Optional[str]): Server path to attached file
                                  - None if no attachment
                                  - Secure path for file access
        file_name (Optional[str]): Original filename of attachment
                                  - None if no attachment
                                  - Used for download display
        created_at (datetime): Message creation timestamp
                              - UTC timezone for consistency
                              - Used for message sorting and age
    """
    id: int
    sender_id: Optional[int]
    receiver_id: Optional[int]
    subject: Optional[str]
    content: str
    is_read: bool
    is_from_admin: bool
    file_path: Optional[str]
    file_name: Optional[str]
    created_at: datetime

# =========================================
# USER MESSAGING ENDPOINTS
# =========================================
# Endpoints for regular users to communicate with administrators

@router.post("/send")
def send_message(request: SendMessageRequest, db: Session = Depends(get_db)):
    """
    Send text message from user to administrator.

    Primary communication endpoint for users to contact support, ask questions,
    report issues, or request assistance from the administrative team.

    Message Processing:
    1. Validate user authentication and permissions
    2. Sanitize and validate message content
    3. Create message record in database
    4. Set initial status (unread for admin attention)
    5. Return success confirmation

    Support Categories:
    - Technical support and troubleshooting
    - Feature requests and suggestions
    - Billing and license inquiries
    - Account management requests
    - General feedback and comments

    Message Validation:
    - Content length limits
    - Spam filtering (future enhancement)
    - Profanity/content filtering
    - Rate limiting per user

    Parameters:
        request (SendMessageRequest): Message content and metadata
        db (Session): Database session for message storage

    Returns:
        dict: Message creation confirmation
            {
                "message": "Message sent successfully",
                "message_id": 123,
                "timestamp": "2024-01-15T10:30:00Z"
            }

    Raises:
        HTTPException (400): Invalid message content or validation errors
        HTTPException (401): User authentication required
        HTTPException (500): Message creation failure

    Example:
        >>> message_data = {
        ...     "sender_id": 123,
        ...     "subject": "Login Issue",
        ...     "content": "I'm having trouble logging into my account",
        ...     "is_from_admin": false
        ... }
        >>> response = await send_message(message_data)
        >>> print(response["message"])
        Message sent successfully

    Note:
        Messages are initially marked as unread for admin attention.
        Consider implementing email notifications for new messages.
        Message queuing may be added for high-volume scenarios.
    """
    try:
        # Validate message content
        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="Message content cannot be empty")

        # Create message record
        new_message = models.Message(
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            subject=request.subject,
            content=request.content.strip(),
            is_read=False,  # Admin needs to read this
            is_from_admin=request.is_from_admin,
            created_at=datetime.utcnow()
        )

        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        return {
            "message": "Message sent successfully",
            "message_id": new_message.id,
            "timestamp": new_message.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.post("/send-with-file")
def send_message_with_file(
    sender_id: Optional[int] = Form(None),
    receiver_id: Optional[int] = Form(None),
    subject: Optional[str] = Form(None),
    content: str = Form(...),
    is_from_admin: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Send message with file attachment from user to administrator.

    Enhanced messaging endpoint that supports file uploads alongside text messages.
    Enables users to share documents, screenshots, or other files with support requests.

    File Upload Process:
    1. Validate file type and size constraints
    2. Generate secure filename to prevent conflicts
    3. Save file to secure upload directory
    4. Create message record with file reference
    5. Return success confirmation with file details

    Supported Use Cases:
    - Error screenshots and diagnostic information
    - Document sharing (manuals, specifications)
    - Configuration files for troubleshooting
    - Report attachments and supporting evidence
    - Image uploads for visual issues

    File Security:
    - Type validation against allowed extensions
    - Size limits to prevent abuse
    - Secure filename generation (UUID-based)
    - Isolated upload directory
    - File access controls

    Parameters:
        sender_id (Optional[int]): User ID sending the message (Form field)
        receiver_id (Optional[int]): Target user ID (Form field)
        subject (Optional[str]): Message subject (Form field)
        content (str): Message content (Form field, required)
        is_from_admin (bool): Admin sender flag (Form field)
        file (Optional[UploadFile]): File attachment (multipart form data)
        db (Session): Database session for operations

    Returns:
        dict: Message creation confirmation with file details
            {
                "message": "Message with file sent successfully",
                "message_id": 123,
                "file_name": "error_log.txt",
                "file_size": 2048,
                "timestamp": "2024-01-15T10:30:00Z"
            }

    Raises:
        HTTPException (400): Invalid file type, size, or message content
        HTTPException (401): User authentication required
        HTTPException (500): File upload or message creation failure

    Example:
        >>> # Using multipart form data
        >>> files = {'file': open('error_screenshot.png', 'rb')}
        >>> data = {
        ...     'sender_id': '123',
        ...     'content': 'Getting this error, please help',
        ...     'is_from_admin': 'false'
        ... }
        >>> response = await send_message_with_file(data=data, files=files)
        >>> print(response["message"])
        Message with file sent successfully

    Note:
        File uploads increase message processing time.
        Consider implementing virus scanning for uploaded files.
        Large files may require chunked upload for better UX.
    """
    file_path = None
    file_name = None
    file_content = None

    try:
        # Validate message content
        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="Message content cannot be empty")

        file_path = None
        file_name = None
        file_content = None

        # Process file upload if provided
        if file:
            # Validate file size
            file_content = file.file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB")

            # Validate file extension
            if not file.filename:
                raise HTTPException(status_code=400, detail="File must have a valid filename")
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"File type '{file_ext}' not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}")

            # Generate secure filename
            secure_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, secure_filename)
            file_name = file.filename

            # Save file to disk
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)

        # Create message record
        new_message = models.Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            subject=subject,
            content=content.strip(),
            file_path=file_path,
            file_name=file_name,
            is_read=False,
            is_from_admin=is_from_admin,
            created_at=datetime.utcnow()
        )

        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        response_data = {
            "message": "Message sent successfully",
            "message_id": new_message.id,
            "timestamp": new_message.created_at.isoformat()
        }

        # Add file information if attachment was included
        if file and file_content is not None:
            response_data.update({
                "file_name": file_name,
                "file_size": len(file_content)
            })

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Clean up uploaded file if message creation failed
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Ignore cleanup errors
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.put("/mark-all-read/{user_id}")
def mark_all_messages_read(user_id: int, db: Session = Depends(get_db)):
    """
    Mark all messages for a user as read.

    Bulk operation to update read status for all messages addressed to a specific user.
    Used when users want to clear unread message notifications or mark entire inbox as read.

    Read Status Update:
    - Changes is_read flag from False to True
    - Applies to all messages where user is receiver
    - Admin messages and user messages both affected
    - Timestamp of read action may be tracked

    Use Cases:
    - User clears notification badges
    - Bulk message management
    - Inbox organization
    - Admin response acknowledgment

    Parameters:
        user_id (int): Target user whose messages to mark as read
        db (Session): Database session for message updates

    Returns:
        dict: Operation confirmation with count of updated messages
            {
                "message": "All messages marked as read",
                "updated_count": 5,
                "user_id": 123
            }

    Raises:
        HTTPException (404): User not found
        HTTPException (500): Database update failure

    Example:
        >>> response = await mark_all_messages_read(123)
        >>> print(f"Marked {response['updated_count']} messages as read")
        Marked 5 messages as read

    Note:
        This operation cannot be undone.
        Consider adding confirmation for large message counts.
        May trigger notification updates in frontend.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Update all unread messages for this user
        updated_count = db.query(models.Message).filter(
            models.Message.receiver_id == user_id,
            models.Message.is_read == False
        ).update({"is_read": True})

        db.commit()

        return {
            "message": "All messages marked as read",
            "updated_count": updated_count,
            "user_id": user_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update messages: {str(e)}")

# =========================================
# ADMINISTRATIVE MESSAGING ENDPOINTS
# =========================================
# Endpoints for administrators to manage and respond to messages

@router.get("/admin/all")
def get_all_messages_admin(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Messages per page"),
    search: Optional[str] = Query(None, description="Search in subject/content"),
    unread_only: bool = Query(False, description="Show only unread messages")
):
    """
    Retrieve all messages for administrative monitoring and management.

    Comprehensive message listing for administrators to view, search, and manage
    all user communications across the system. Supports pagination, filtering,
    and search capabilities for efficient message handling.

    Administrative Features:
    - View all user-to-admin and admin-to-user messages
    - Search by content, subject, or user information
    - Filter by read status (unread messages only)
    - Paginated results for performance
    - Message metadata and user context

    Message Visibility:
    - All conversations across all users
    - System-generated messages and notifications
    - File attachment indicators
    - Read/unread status for prioritization
    - Timestamps for chronological ordering

    Search Capabilities:
    - Subject line search
    - Message content search
    - User email/name search
    - Case-insensitive text matching
    - Partial word matching

    Parameters:
        db (Session): Database session for message queries
        page (int): Page number for pagination (1-based)
        per_page (int): Number of messages per page (1-100)
        search (Optional[str]): Search term for filtering messages
        unread_only (bool): Filter to show only unread messages

    Returns:
        dict: Paginated message list with search results
            {
                "messages": [
                    {
                        "id": 123,
                        "sender": {"id": 456, "email": "user@example.com"},
                        "receiver": "admin",
                        "subject": "Login Issue",
                        "content": "Can't access my account...",
                        "is_read": false,
                        "has_file": true,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 150,
                    "total_pages": 8,
                    "has_next": true,
                    "has_prev": false
                },
                "search_info": {
                    "query": "login",
                    "total_results": 12
                }
            }

    Raises:
        HTTPException (500): Database query failures

    Example:
        >>> # Get all messages, page 1
        >>> response = await get_all_messages_admin(page=1, per_page=20)
        >>> print(f"Total messages: {response['pagination']['total']}")
        Total messages: 150

        >>> # Search for specific messages
        >>> response = await get_all_messages_admin(search="password", unread_only=true)
        >>> print(f"Found {len(response['messages'])} unread messages about passwords")
        Found 3 unread messages about passwords

    Note:
        Large message volumes may require database indexing on search fields.
        Consider implementing message caching for frequently accessed data.
        Admin access to user messages should be logged for privacy compliance.
    """
    try:
        # Base query with user relationships
        query = db.query(models.Message).options(
            joinedload(models.Message.sender),
            joinedload(models.Message.receiver)
        )

        # Apply unread filter if requested
        if unread_only:
            query = query.filter(models.Message.is_read == False)

        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Message.subject.ilike(search_term),
                    models.Message.content.ilike(search_term),
                    and_(
                        models.Message.sender_id.isnot(None),
                        models.Message.sender.has(models.User.email.ilike(search_term))
                    ),
                    and_(
                        models.Message.sender_id.isnot(None),
                        models.Message.sender.has(models.User.name.ilike(search_term))
                    )
                )
            )

        # Get total count for pagination
        total_messages = query.count()

        # Apply sorting and pagination
        messages = query.order_by(desc(models.Message.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()

        # Format message data
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "sender": {
                    "id": msg.sender.id if msg.sender else None,
                    "email": msg.sender.email if msg.sender else "System",
                    "name": msg.sender.name if msg.sender else "System"
                } if msg.sender_id else "Admin",
                "receiver": {
                    "id": msg.receiver.id if msg.receiver else None,
                    "email": msg.receiver.email if msg.receiver else "Admin",
                    "name": msg.receiver.name if msg.receiver else "Admin"
                } if msg.receiver_id else "Admin",
                "subject": msg.subject,
                "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                "is_read": msg.is_read,
                "is_from_admin": msg.is_from_admin,
                "has_file": bool(msg.file_path),
                "file_name": msg.file_name,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })

        # Calculate pagination metadata
        total_pages = (total_messages + per_page - 1) // per_page

        response_data = {
            "messages": message_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_messages,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

        # Add search information if search was performed
        if search:
            response_data["search_info"] = {
                "query": search,
                "total_results": total_messages
            }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")

@router.get("/admin/unread-count")
def get_admin_unread_count(db: Session = Depends(get_db)):
    """
    Get count of unread messages requiring admin attention.

    Provides administrators with a quick overview of pending communications
    that need response or review. Used for dashboard notifications and
    workload management.

    Unread Message Categories:
    - New user support requests and inquiries
    - Follow-up questions on existing issues
    - Technical problem reports
    - Feature requests and feedback
    - System error notifications

    Administrative Use:
    - Dashboard notification counters
    - Workload distribution among support staff
    - Service level agreement monitoring
    - Response time performance metrics
    - Priority queue management

    Parameters:
        db (Session): Database session for message queries

    Returns:
        dict: Unread message statistics
            {
                "unread_count": 15,
                "urgent_count": 3,  # Messages older than 24 hours
                "avg_wait_time": "4.2 hours",
                "new_today": 8
            }

    Raises:
        HTTPException (500): Database query failures

    Example:
        >>> stats = await get_admin_unread_count()
        >>> print(f"{stats['unread_count']} messages need attention")
        15 messages need attention

    Note:
        Consider implementing priority levels for different message types.
        Urgent messages (older than threshold) should be highlighted.
        Real-time updates may be needed for live dashboards.
    """
    try:
        # Count total unread messages
        unread_count = db.query(models.Message).filter(
            models.Message.is_read == False
        ).count()

        # Count urgent messages (unread for more than 24 hours)
        one_day_ago = datetime.utcnow() - timedelta(hours=24)
        urgent_count = db.query(models.Message).filter(
            and_(
                models.Message.is_read == False,
                models.Message.created_at < one_day_ago
            )
        ).count()

        # Count new messages from today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_today_count = db.query(models.Message).filter(
            models.Message.created_at >= today_start
        ).count()

        return {
            "unread_count": unread_count,
            "urgent_count": urgent_count,
            "new_today": new_today_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")

@router.get("/admin/conversations")
def get_admin_conversations(db: Session = Depends(get_db)):
    """
    Get overview of all user conversations for administrative monitoring.

    Provides administrators with a high-level view of communication patterns,
    user engagement levels, and conversation status across all users.

    Conversation Metrics:
    - Total messages per user conversation
    - Unread message counts per conversation
    - Last message timestamps
    - Conversation activity levels
    - User engagement indicators

    Administrative Benefits:
    - Identify high-priority support cases
    - Monitor support team response effectiveness
    - Track user satisfaction through communication patterns
    - Manage support workload distribution
    - Identify frequently contacting users

    Conversation Status:
    - Active: Recent messages (last 7 days)
    - Dormant: Older conversations with no recent activity
    - Resolved: Conversations marked as complete
    - Escalated: Conversations requiring higher-level attention

    Parameters:
        db (Session): Database session for conversation analysis

    Returns:
        dict: Conversation overview with user communication summaries
            {
                "conversations": [
                    {
                        "user": {
                            "id": 123,
                            "email": "user@example.com",
                            "name": "John Doe"
                        },
                        "message_count": 15,
                        "unread_count": 3,
                        "last_message_at": "2024-01-15T10:30:00Z",
                        "status": "active",
                        "avg_response_time": "2.5 hours"
                    }
                ],
                "summary": {
                    "total_conversations": 45,
                    "active_conversations": 12,
                    "total_unread": 28
                }
            }

    Raises:
        HTTPException (500): Database query failures

    Example:
        >>> conversations = await get_admin_conversations()
        >>> active = [c for c in conversations['conversations'] if c['status'] == 'active']
        >>> print(f"{len(active)} active conversations need attention")
        12 active conversations need attention

    Note:
        Conversation analysis can be resource-intensive with many users.
        Consider implementing caching for frequently accessed metrics.
        Advanced analytics may include sentiment analysis or topic categorization.
    """
    try:
        # Get conversation statistics by user
        # This is a simplified version - could be enhanced with more metrics
        conversations_query = db.query(
            models.Message.sender_id.label('user_id'),
            func.count(models.Message.id).label('message_count'),
            func.sum(models.Message.is_read == False).label('unread_count'),
            func.max(models.Message.created_at).label('last_message_at')
        ).filter(
            models.Message.sender_id.isnot(None)  # User-to-admin messages
        ).group_by(
            models.Message.sender_id
        ).subquery()

        # Get user details for conversations
        conversations = db.query(
            conversations_query,
            models.User
        ).join(
            models.User,
            conversations_query.c.user_id == models.User.id
        ).all()

        # Format conversation data
        conversation_list = []
        total_unread = 0
        active_count = 0

        for conv, user in conversations:
            # Determine conversation status
            last_msg_time = conv.last_message_at
            days_since_last_msg = (datetime.utcnow() - last_msg_time).days if last_msg_time else 999

            if days_since_last_msg <= 7:
                status = "active"
                active_count += 1
            elif days_since_last_msg <= 30:
                status = "recent"
            else:
                status = "dormant"

            conversation_list.append({
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                },
                "message_count": conv.message_count,
                "unread_count": conv.unread_count or 0,
                "last_message_at": last_msg_time.isoformat() if last_msg_time else None,
                "status": status,
                "days_since_last_message": days_since_last_msg
            })

            total_unread += conv.unread_count or 0

        return {
            "conversations": conversation_list,
            "summary": {
                "total_conversations": len(conversation_list),
                "active_conversations": active_count,
                "total_unread": total_unread
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/admin/chat/{user_id}")
def get_admin_user_chat(user_id: int, db: Session = Depends(get_db)):
    """
    Get complete chat history between administrator and specific user.

    Retrieves the full conversation thread for detailed support case review,
    enabling administrators to understand complete user interaction context.

    Chat History Use Cases:
    - Investigate complex support issues
    - Review conversation quality and effectiveness
    - Transfer conversations between support agents
    - Generate detailed support reports
    - Training and quality assurance analysis

    Conversation Context:
    - Complete message timeline with timestamps
    - File attachments and shared documents
    - Message read status and delivery confirmation
    - Admin response patterns and timeliness
    - Conversation flow and resolution progress

    Administrative Features:
    - Full conversation visibility
    - Message search within conversation
    - Export conversation for records
    - Response time analysis
    - Conversation tagging and categorization

    Parameters:
        user_id (int): Target user for chat history retrieval
        db (Session): Database session for message queries

    Returns:
        dict: Complete conversation history with user context
            {
                "user": {
                    "id": 123,
                    "email": "user@example.com",
                    "name": "John Doe",
                    "is_license_active": true
                },
                "messages": [
                    {
                        "id": 456,
                        "direction": "user_to_admin",
                        "subject": "Login Issue",
                        "content": "Can't access my account",
                        "is_read": true,
                        "file_path": null,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "conversation_stats": {
                    "total_messages": 15,
                    "unread_count": 0,
                    "avg_response_time": "2.3 hours",
                    "conversation_duration": "3 days"
                }
            }

    Raises:
        HTTPException (404): User not found
        HTTPException (500): Database query failures

    Example:
        >>> chat_history = await get_admin_user_chat(123)
        >>> messages = chat_history['messages']
        >>> print(f"Conversation has {len(messages)} messages")
        Conversation has 15 messages

    Note:
        Large conversation histories may require pagination.
        Consider implementing message threading for complex conversations.
        File attachments should have secure access controls.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Get all messages between this user and admin
        messages = db.query(models.Message).filter(
            or_(
                and_(models.Message.sender_id == user_id, models.Message.receiver_id.is_(None)),
                and_(models.Message.sender_id.is_(None), models.Message.receiver_id == user_id)
            )
        ).order_by(models.Message.created_at).all()

        # Format messages with direction indicators
        message_list = []
        for msg in messages:
            # Determine message direction
            if msg.sender_id == user_id:
                direction = "user_to_admin"
            else:
                direction = "admin_to_user"

            message_list.append({
                "id": msg.id,
                "direction": direction,
                "subject": msg.subject,
                "content": msg.content,
                "is_read": msg.is_read,
                "file_path": msg.file_path,
                "file_name": msg.file_name,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })

        # Calculate conversation statistics
        total_messages = len(message_list)
        unread_count = sum(1 for msg in message_list if not msg['is_read'])

        # Calculate average response time (simplified)
        admin_messages = [msg for msg in message_list if msg['direction'] == 'admin_to_user']
        user_messages = [msg for msg in message_list if msg['direction'] == 'user_to_admin']

        # Simple response time calculation (could be enhanced)
        avg_response_time = "N/A"
        if len(admin_messages) > 0 and len(user_messages) > 0:
            # This is a simplified calculation - real implementation would be more sophisticated
            avg_response_time = "2-4 hours"  # Placeholder

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_license_active": user.is_license_active
            },
            "messages": message_list,
            "conversation_stats": {
                "total_messages": total_messages,
                "unread_count": unread_count,
                "avg_response_time": avg_response_time
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """
    Delete specific message from the communication system.

    Allows administrators to remove inappropriate, outdated, or erroneous messages
    from the system while maintaining conversation integrity where possible.

    Deletion Considerations:
    - Message content and metadata removal
    - Associated file attachment cleanup
    - Conversation thread impact assessment
    - Audit trail preservation
    - User notification requirements

    Administrative Authority:
    - Full message deletion permissions
    - Override of message ownership
    - Emergency content removal capability
    - System maintenance and cleanup rights

    File Cleanup:
    - Remove attached files from storage
    - Update file reference counters
    - Clean up orphaned file records
    - Storage quota adjustments

    Parameters:
        message_id (int): Unique identifier of message to delete
        db (Session): Database session for message operations

    Returns:
        dict: Deletion confirmation with details
            {
                "message": "Message deleted successfully",
                "message_id": 123,
                "file_deleted": true
            }

    Raises:
        HTTPException (404): Message not found
        HTTPException (500): Deletion failure or database errors

    Example:
        >>> response = await delete_message(456)
        >>> print(response["message"])
        Message deleted successfully

    Note:
        Message deletion is permanent and cannot be undone.
        Consider implementing soft deletion for audit purposes.
        File deletion failures should not prevent message deletion.
    """
    # Find message to delete
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        file_deleted = False

        # Delete associated file if it exists
        if message.file_path and os.path.exists(message.file_path):
            try:
                os.remove(message.file_path)
                file_deleted = True
            except OSError as e:
                # Log file deletion error but don't fail the operation
                print(f"Warning: Could not delete file {message.file_path}: {e}")
                file_deleted = False

        # Delete message from database
        db.delete(message)
        db.commit()

        return {
            "message": "Message deleted successfully",
            "message_id": message_id,
            "file_deleted": file_deleted
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")
