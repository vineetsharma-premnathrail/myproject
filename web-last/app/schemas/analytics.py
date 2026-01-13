"""
User Analytics and Session Schemas Module
----------------------------------------
Purpose:
    Defines Pydantic models for user sessions, tool usage patterns,
    and analytics data structures.
Layer:
    Backend / Schemas / Analytics
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSessionBase(BaseModel):
    """
    Base user session model for tracking technical data.

    Contains essential session information for analytics and security monitoring.
    """
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    browser_type: Optional[str] = None
    device_type: Optional[str] = None
    operating_system: Optional[str] = None
    location: Optional[str] = None


class UserSessionResponse(UserSessionBase):
    """
    User session response model with session metadata.
    """
    id: int
    user_id: int
    session_token: str
    is_active: bool
    login_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    logout_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ToolUsageBase(BaseModel):
    """
    Base tool usage model for tracking usage patterns.
    """
    tool_name: str
    usage_count: int = 1
    total_calculations: int = 0
    average_session_time: Optional[int] = None


class ToolUsageResponse(ToolUsageBase):
    """
    Tool usage response model with usage metadata.
    """
    id: int
    user_id: int
    last_used: Optional[datetime] = None
    first_used: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserAnalytics(BaseModel):
    """
    Comprehensive user analytics data for admin dashboard.
    """
    user_id: int
    email: str
    name: Optional[str] = None
    total_sessions: int = 0
    total_calculations: int = 0
    most_used_tool: Optional[str] = None
    average_session_duration: Optional[int] = None
    last_activity: Optional[datetime] = None
    registration_date: Optional[datetime] = None
    license_status: str = "inactive"
    license_type: Optional[str] = None
    license_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True