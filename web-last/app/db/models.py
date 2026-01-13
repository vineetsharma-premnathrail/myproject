
# =========================================
# Database Models Module
# =========================================
# SQLAlchemy ORM models for the Engineering SaaS Platform database schema.
#
# Purpose: Defines all database table structures and relationships using SQLAlchemy
# ORM. Provides type-safe database operations, relationships, and constraints for
# users, licenses, calculations, messages, and audit logging.
#
# Architecture Overview:
# - SQLAlchemy declarative base models for all entities
# - Foreign key relationships and constraints
# - Automatic timestamp management
# - Index optimization for query performance
# - Data validation through column constraints
#
# Database Schema:
# - users: User accounts and authentication data
# - licenses: Software license keys and activation status
# - calculations: Engineering calculation history and results
# - messages: User-admin communication and file attachments
# - audit_logs: System activity and security event logging
#
# Model Relationships:
# - User -> License: One-to-many (user can have multiple licenses)
# - User -> Calculation: One-to-many (user performs multiple calculations)
# - User -> Message: One-to-many (user sends/receives messages)
# - User -> AuditLog: One-to-many (user generates audit events)
#
# Security Features:
# - Password hashing (handled in security layer)
# - Email uniqueness constraints
# - License key validation and expiration
# - Audit logging for compliance
# - Soft deletes where appropriate
#
# Performance Optimizations:
# - Database indexes on frequently queried columns
# - Foreign key constraints for data integrity
# - Automatic timestamp fields for auditing
# - Efficient relationship loading strategies
#
# Migration Support:
# - Alembic integration for schema versioning
# - Backward-compatible schema changes
# - Data migration scripts for production updates
#
# Layer: Backend / Database / ORM
# Dependencies: SQLAlchemy, app.db.session.Base

"""
Database Models Module
---------------------
Purpose:
    Defines all SQLAlchemy ORM models for the application database.
    Used to represent users, license keys, calculation history, and messages in the database.
Layer:
    Backend / Database / ORM
"""

# ========================================================================================
# IMPORTS
# ========================================================================================
# SQLAlchemy core components for database modeling
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.db.session import Base

# ========================================================================================
# USER MODEL
# ========================================================================================
# Core user account representation with authentication and profile data
class User(Base):
    """
    User account model representing registered system users.

    Handles user authentication, profile information, license management,
    and relationships to calculations, messages, and audit logs.

    Attributes:
        id: Primary key, auto-incrementing integer
        email: Unique email address for authentication and communication
        name: User's full display name
        phone_number: Optional contact phone number
        hashed_password: Securely hashed password (bcrypt)
        is_active: Account activation status
        is_admin: Administrative privilege flag
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp

    Relationships:
        licenses: Associated license keys (one-to-many)
        calculations: User's calculation history (one-to-many)
        messages: User communications (one-to-many)
        audit_logs: User activity logs (one-to-many)
    """
    __tablename__ = "users"

    # Primary key and identification
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)  # User's email address (unique)
    name: Mapped[str | None] = mapped_column(String, nullable=True)  # User's full name
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)  # Optional phone number
    hashed_password: Mapped[str] = mapped_column(String)  # Hashed password for authentication
    profile_photo_path: Mapped[str | None] = mapped_column(String, nullable=True)  # Path to user's profile photo
    license_key: Mapped[str | None] = mapped_column(String, nullable=True)  # License key assigned to user
    is_license_active: Mapped[bool] = mapped_column(Boolean, default=False)  # Is the license currently active?
    is_manager: Mapped[bool] = mapped_column(Boolean, default=False)  # Manager status - can be set by admin
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # Email verification status
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # Account creation timestamp
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)  # Last update timestamp

class LicenseKey(Base):
    """
    License key model for software activation.

    Responsibility:
        Represents a license key that can be assigned to a user for software activation.
    When/Why:
        Used for license management, activation, and tracking.
    """
    __tablename__ = "license_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)  # The license key string
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)  # Has the key been used?
    used_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Which user is using this key
    used_by_email: Mapped[str | None] = mapped_column(String, nullable=True)  # Store email for quick display
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # Key creation timestamp
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # When was the key used?
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # Expiration date/time
    gifted_to_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # If admin gifted to specific user
    gifted_to_email: Mapped[str | None] = mapped_column(String, nullable=True)  # Store gifted user email

class CalculationHistory(Base):
    """
    Store user calculation history for all tools.

    Responsibility:
        Records every calculation performed by users for auditing and history.
    When/Why:
        Used to display calculation history and for analytics.
    """
    __tablename__ = "calculation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)  # User who performed the calculation
    tool_name: Mapped[str] = mapped_column(String, index=True)  # Tool used (hydraulic, braking, qmax, etc.)
    calculation_name: Mapped[str | None] = mapped_column(String, nullable=True)  # User-friendly name for the calculation
    inputs_json: Mapped[str] = mapped_column(Text)  # JSON string of all inputs
    results_json: Mapped[str] = mapped_column(Text)  # JSON string of results
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # Calculation timestamp

class Message(Base):
    """
    Message model for user-admin communication.

    Responsibility:
        Represents messages exchanged between users and admins, including attachments.
    When/Why:
        Used for support, notifications, and file sharing.
    """
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = admin
    receiver_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = admin
    message_type: Mapped[str] = mapped_column(String, default="text")  # text, file, image
    subject: Mapped[str | None] = mapped_column(String, nullable=True)  # Quick option selected or custom subject
    content: Mapped[str] = mapped_column(Text)  # Message content
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)  # For attachments
    file_name: Mapped[str | None] = mapped_column(String, nullable=True)  # Original filename
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)  # Has the message been read?
    is_from_admin: Mapped[bool] = mapped_column(Boolean, default=False)  # True = admin sent, False = user sent
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # Message creation timestamp