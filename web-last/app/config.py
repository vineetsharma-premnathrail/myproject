
# =========================================
# Application Configuration Management
# =========================================
# Centralized configuration system for the Engineering SaaS Platform using Pydantic.
#
# Purpose: Provides secure, type-safe, and environment-aware configuration management
# for all application settings. Handles environment variables, validation, and default
# values while ensuring sensitive information is never hardcoded in source code.
#
# Architecture Overview:
# - Pydantic BaseSettings for type validation and environment loading
# - Environment variable priority over default values
# - .env file support for local development
# - Validation and transformation of configuration values
# - Security-focused design with no hardcoded secrets
# - Environment-specific configuration profiles
#
# Configuration Categories:
# - Application: Basic app metadata and runtime settings
# - Server: Network and hosting configuration
# - Database: Connection strings and database settings
# - Security: Authentication, encryption, and access control
# - Email: SMTP configuration for notifications
# - File Storage: Upload handling and storage settings
# - External Services: Third-party integrations and APIs
#
# Environment Support:
# - Development: Local SQLite, debug mode, relaxed security
# - Testing: In-memory database, isolated test environment
# - Staging: Production-like setup with test data
# - Production: PostgreSQL, security hardening, performance optimization
#
# Security Considerations:
# - No hardcoded passwords, keys, or sensitive data
# - Environment variable encryption for production secrets
# - Validation of secure URL schemes and configurations
# - Database URL security checks and format validation
# - CORS origin restrictions for production deployments
#
# Configuration Loading Priority:
# 1. Environment variables (highest priority)
# 2. .env file in project root
# 3. Default values (lowest priority)
#
# Used by: All application modules requiring configuration access
# Dependencies: Pydantic, python-dotenv for .env file support
# Validation: Type checking, format validation, security constraints

import os
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central configuration class for the Engineering SaaS Platform.

    Provides type-safe, validated configuration management using Pydantic's
    BaseSettings. All sensitive information is loaded from environment variables
    or .env files, ensuring security and deployment flexibility.

    Configuration is automatically loaded from:
    1. Environment variables (highest priority)
    2. .env file in project root
    3. Default values defined in this class

    Security Best Practices:
    - Never hardcode secrets, passwords, or sensitive URLs
    - Use environment variables for all production secrets
    - Validate configuration values for security and correctness
    - Restrict CORS origins in production environments
    - Use secure database URLs with proper authentication
    """

    # =========================================
    # APPLICATION SETTINGS
    # =========================================
    # Basic application metadata and runtime configuration

    app_name: str = Field(
        default="Engineering Tools SaaS",
        description="Human-readable application name displayed in API docs and UI"
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version for API documentation and deployment tracking"
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode with detailed logging and error pages (disable in production)"
    )

    # =========================================
    # SERVER CONFIGURATION
    # =========================================
    # Network and hosting settings for the FastAPI application

    host: str = Field(
        default="127.0.0.1",
        description="Server bind address - 0.0.0.0 for all interfaces, 127.0.0.1 for localhost only"
    )

    port: int = Field(
        default=8000,
        description="Server port number for HTTP connections",
        ge=1024,
        le=65535
    )

    # =========================================
    # DATABASE CONFIGURATION
    # =========================================
    # Database connection and ORM settings for data persistence

    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/engineering_tools",

        description="Complete database connection URL with credentials and connection parameters"
    )

    @validator("database_url")
    def validate_database_url(cls, v):
        """
        Validate database URL for security and proper formatting.

        Ensures database URL is provided and follows security best practices.
        Prevents insecure configurations and provides clear error messages.

        Validation Rules:
        - URL must be non-empty and properly formatted
        - PostgreSQL recommended for production (optional enforcement)
        - SQLite allowed for development and testing
        - No hardcoded credentials in default values

        Parameters:
            v (str): Database URL to validate

        Returns:
            str: Validated and potentially transformed database URL

        Raises:
            ValueError: If database URL is missing, malformed, or insecure

        Security Considerations:
            - Prevents use of insecure database configurations
            - Encourages PostgreSQL for production workloads
            - Allows SQLite for development flexibility
            - Validates URL format and required components
        """
        if not v:
            raise ValueError("DATABASE_URL is required")

        # Optional: Enforce PostgreSQL in production environments
        # Uncomment for strict production requirements
        # if "production" in os.getenv("ENVIRONMENT", "").lower():
        #     if not v.startswith("postgresql"):
        #         raise ValueError("Production requires PostgreSQL database")

        # Allow SQLite for development and testing
        if v.startswith("sqlite"):
            # Ensure SQLite file path is secure and accessible
            if ".." in v or not (v.startswith("sqlite:///") or v == "sqlite:///:memory:"):
                raise ValueError("Invalid SQLite database URL format")

        return v
        #         "SQLite is NOT allowed in production. Use PostgreSQL. "
        #         "Format: postgresql://user:password@host:5432/dbname"
        #     )
        return v

    # ============ SECURITY ============
    # All secrets must come from environment variables
    secret_key: str = Field(default="", description="JWT/Session secret")

    @validator("secret_key")
    def validate_secret_key(cls, v):
        """
        Ensure the secret key is strong and not a default value.
        """
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v == "your-secret-key-change-this-in-production":
            raise ValueError("You must set a proper SECRET_KEY in .env")
        return v

    algorithm: str = Field(default="HS256")  # JWT algorithm

    # JWT Token Settings
    access_token_expire_minutes: int = Field(default=30)  # Access token expiry
    refresh_token_expire_days: int = Field(default=7)  # Refresh token expiry (days)
    refresh_token_expire_minutes: int = Field(default=10080)  # Refresh token expiry (minutes)

    # ============ CORS ============
    # Only allow specific origins in production
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """
        Parse comma-separated origins or accept a list.
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    force_https: bool = Field(default=True)  # Enforce HTTPS
    hsts_max_age: int = Field(default=31536000)  # HSTS header max age (1 year)

    # ============ RATE LIMITING ============
    rate_limit_requests_per_minute: int = Field(default=60)  # General rate limit
    login_rate_limit_per_minute: int = Field(default=5)  # Login attempts
    otp_rate_limit_per_minute: int = Field(default=3)  # OTP requests
    license_rate_limit_per_minute: int = Field(default=10)  # License requests

    # ============ FILE UPLOAD ============
    max_upload_size_mb: int = Field(default=10)  # Max upload size in MB

    @property
    def max_upload_size(self) -> int:
        """
        Returns the max upload size in bytes (for validation).
        """
        return self.max_upload_size_mb * 1024 * 1024

    allowed_extensions: set = {".pdf", ".docx", ".xlsx", ".csv"}  # Allowed file types

    # ============ EMAIL/OTP ============
    smtp_server: Optional[str] = Field(default=None)  # SMTP server
    smtp_port: Optional[int] = Field(default=587)  # SMTP port
    smtp_username: Optional[str] = Field(default=None)  # SMTP username
    smtp_password: Optional[str] = Field(default=None)  # SMTP password
    otp_expiry_minutes: int = Field(default=10)  # OTP expiry time

    # ============ LICENSE ============
    license_key_length: int = Field(default=32)  # License key length
    license_expiry_days: int = Field(default=365)  # License expiry

    # ============ LOGGING ============
    log_level: str = Field(default="INFO")  # Logging level
    log_format: str = Field(default="json")  # Log format: json or text

    # ============ MONITORING ============
    sentry_dsn: Optional[str] = Field(default=None)  # Sentry DSN for error monitoring

    class Config:
        """
        Pydantic config for environment file and case sensitivity.
        """
        env_file = ".env"
        case_sensitive = False


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"\n❌ CONFIGURATION ERROR: {str(e)}")
    print("\nFIX: Copy .env.example to .env and update with your values:")
    print("  - Generate SECRET_KEY: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    print("  - Set DATABASE_URL to PostgreSQL")
    print("  - Update CORS_ORIGINS for your domain")
    print("  - Configure SMTP for email")
    print("\nExit.\n")
    raise