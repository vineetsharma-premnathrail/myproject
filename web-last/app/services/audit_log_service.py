"""
Audit Log Service Module
-----------------------
Purpose:
    Provides business logic for recording and retrieving audit logs of user and system actions.
    Used by API endpoints and background tasks to track important events for security and compliance.
    Currently implements console-based logging; designed to be extended with database persistence.
Layer:
    Backend / Services / Audit Log
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import app.db.models as models


class AuditLogService:
    """
    Service for logging and auditing system events.

    Provides centralized logging for user actions, calculations, authentication events,
    and license operations. Currently logs to console but designed for database storage.

    Note: This is a placeholder implementation. In production, logs should be stored
    in a dedicated audit table with proper indexing and retention policies.
    """

    @staticmethod
    def log_user_action(
        db: Session,
        user_id: int,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log a generic user action for audit purposes.

        Creates a structured log entry for any user-initiated action in the system.
        Useful for security monitoring, compliance reporting, and debugging.

        Args:
            db: Database session (reserved for future database logging)
            user_id: ID of the user performing the action
            action: Type of action (e.g., "create", "update", "delete", "login")
            resource: Resource being acted upon (e.g., "user", "calculation", "license")
            details: Optional additional context or data about the action
            ip_address: Client IP address for security tracking

        Note:
            Currently prints to console. Replace with database insertion in production.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address
        }

        print(f"AUDIT: {json.dumps(log_entry)}")

    @staticmethod
    def log_calculation(
        db: Session,
        user_id: int,
        tool_name: str,
        inputs: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """
        Log a calculation request for audit and usage tracking.

        Records when users perform engineering calculations using the various tools.
        Helps track tool usage patterns and provides audit trail for calculations.

        Args:
            db: Database session (reserved for future database logging)
            user_id: ID of the user performing the calculation
            tool_name: Name of the calculation tool used (e.g., "braking", "hydraulic")
            inputs: Input parameters provided to the calculation
            ip_address: Client IP address for security tracking
        """
        AuditLogService.log_user_action(
            db=db,
            user_id=user_id,
            action="calculation",
            resource=f"tool:{tool_name}",
            details={"inputs": inputs},
            ip_address=ip_address
        )

    @staticmethod
    def log_login(
        db: Session,
        user_id: int,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """
        Log a login attempt for security monitoring.

        Records both successful and failed login attempts to help detect
        suspicious activity and provide audit trail for authentication events.

        Args:
            db: Database session (reserved for future database logging)
            user_id: ID of the user attempting login
            success: Whether the login attempt was successful
            ip_address: Client IP address for security tracking
        """
        AuditLogService.log_user_action(
            db=db,
            user_id=user_id,
            action="login",
            resource="auth",
            details={"success": success},
            ip_address=ip_address
        )

    @staticmethod
    def log_license_activation(
        db: Session,
        user_id: int,
        license_key: str,
        ip_address: Optional[str] = None
    ):
        """
        Log license key activation for compliance and usage tracking.

        Records when users activate license keys, helping track license usage
        and provide audit trail for licensing operations.

        Args:
            db: Database session (reserved for future database logging)
            user_id: ID of the user activating the license
            license_key: The license key being activated (masked for security)
            ip_address: Client IP address for security tracking
        """
        AuditLogService.log_user_action(
            db=db,
            user_id=user_id,
            action="license_activate",
            resource="license",
            details={"license_key": license_key},
            ip_address=ip_address
        )