
# =========================================
# FastAPI Application Entrypoint
# =========================================
# Project root entry point for running the Engineering SaaS Platform.
#
# Purpose: Provides the main application entry point for development and production
# deployment. This file serves as the Uvicorn application discovery point, importing
# the FastAPI application instance from the modular app structure.
#
# Architecture Overview:
# - Modular FastAPI application structure
# - Separated application logic in app/ directory
# - Clean separation of concerns (API, business logic, database)
# - Development-friendly entry point with auto-reload capabilities
#
# Application Structure:
# - app/main.py: Core FastAPI application with routes and middleware
# - app/api/: API endpoint modules (auth, users, tools, etc.)
# - app/db/: Database models and session management
# - app/tools/: Engineering calculation tool modules
# - app/services/: Business logic and external integrations
# - app/security/: Authentication and authorization components
#
# Deployment Options:
# 1. Development: uvicorn main:app --reload
# 2. Production: uvicorn main:app --host 0.0.0.0 --port 8000
# 3. Docker: Containerized deployment with gunicorn/uvicorn workers
# 4. Render: Cloud platform deployment with automatic scaling
#
# Environment Configuration:
# - Development: Local SQLite database, debug mode enabled
# - Production: PostgreSQL database, security hardening applied
# - Testing: In-memory database, isolated test environment
#
# Key Features:
# - RESTful API for engineering calculations
# - User authentication and authorization
# - File upload and processing capabilities
# - Admin dashboard and user management
# - Real-time messaging system
# - Comprehensive health monitoring
#
# API Documentation:
# - Interactive Swagger UI: /docs
# - ReDoc Documentation: /redoc
# - OpenAPI Schema: /openapi.json
#
# Usage Examples:
#   # Development with auto-reload
#   uvicorn main:app --reload --host 127.0.0.1 --port 8000
#
#   # Production deployment
#   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
#
#   # Docker container
#   docker run -p 8000:8000 engineering-saas:latest
#
# Dependencies: FastAPI, Uvicorn ASGI server, application modules
# Configuration: Environment variables and config files in app/config.py

# Import the FastAPI application instance from the modular app structure
# This allows Uvicorn to discover and run the application
from app.main import app  # FastAPI application instance