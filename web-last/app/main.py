
# =========================================
# FastAPI Application Core Module
# =========================================
# Central configuration and initialization of the Engineering SaaS Platform.
#
# Purpose: Serves as the main FastAPI application factory and configuration hub.
# Handles application startup, middleware setup, router integration, static file
# serving, and lifecycle event management. This module orchestrates all components
# of the engineering calculation platform into a cohesive web application.
#
# Architecture Overview:
# - FastAPI application instance creation and configuration
# - Middleware stack setup (CORS, security, logging)
# - API router integration and mounting
# - Static asset serving for frontend resources
# - Database initialization and lifecycle management
# - Application event handling (startup/shutdown)
# - Health monitoring and system integration
#
# Application Components:
# - Authentication System: JWT-based user authentication and authorization
# - User Management: Profile management and license administration
# - Engineering Tools: 6 specialized calculation modules (braking, hydraulic, etc.)
# - Messaging System: User-admin communication with file attachments
# - Admin Dashboard: System monitoring and user management interface
# - File Processing: Secure upload handling and report generation
# - Health Monitoring: System status and availability checks
#
# API Structure:
# - /health: System health monitoring endpoints
# - /auth: Authentication and user registration
# - /users: User management and profile operations
# - /tools: Engineering calculation tools and legacy endpoints
# - /history: Calculation history and audit logging
# - /admin: Administrative operations and system management
# - /messages: User messaging and file sharing
# - /assets: Static file serving (HTML, CSS, JS, images)
#
# Middleware Stack:
# - CORS Middleware: Cross-origin resource sharing configuration
# - Authentication Middleware: JWT token validation and user context
# - Logging Middleware: Request/response logging and monitoring
# - Security Middleware: Rate limiting and attack prevention
# - Error Handling: Global exception handling and response formatting
#
# Static Assets:
# - HTML Pages: Frontend interface templates
# - CSS Stylesheets: User interface styling
# - JavaScript: Client-side functionality and API integration
# - Images: Logos, icons, and visual assets
# - Uploads: User-uploaded files and generated reports
#
# Database Integration:
# - Automatic table creation on startup
# - Connection pool management
# - Migration handling and schema updates
# - Session management and transaction handling
#
# Deployment Considerations:
# - Environment-specific configuration loading
# - Production security hardening
# - Performance optimization settings
# - Monitoring and logging configuration
#
# Used by: Uvicorn ASGI server, development tools, deployment scripts
# Dependencies: FastAPI, SQLAlchemy, Pydantic, authentication libraries
# Configuration: Environment variables and settings from app.config

from fastapi import FastAPI  # FastAPI framework for building APIs
from fastapi.middleware.cors import CORSMiddleware  # Middleware for CORS
from fastapi.staticfiles import StaticFiles  # For serving static files
import uvicorn  # ASGI server

# Import application settings and routers
from app.config import settings  # App configuration (env, DB, etc.)
from app.db.session import create_tables  # DB table creation utility
from app.api.health import router as health_router  # Health check endpoints
from app.api.auth import router as auth_router  # Auth endpoints
from app.api.users import router as users_router  # User management endpoints
from app.api.tools import router as tools_router  # Tool calculation endpoints
from app.api.history import router as history_router  # Calculation/user history endpoints
from app.api.admin import router as admin_router  # Admin panel endpoints
from app.api.messages import router as messages_router  # Messaging endpoints
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.utils.logger import logger  # Logger utility

# =========================================
# APPLICATION LIFESPAN MANAGEMENT
# =========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup and shutdown events.
    """
    try:
        # logger.info("Starting Engineering Tools SaaS application")
        create_tables()  # Ensure all DB tables exist
        # logger.info("Database tables created/verified")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        logger.info("Shutting down Engineering Tools SaaS application")

# =========================================
# FASTAPI APPLICATION INSTANCE CREATION
# =========================================
# Create the main FastAPI application with configuration from settings

app = FastAPI(
    title=settings.app_name,  # Application name from config
    version=settings.app_version,  # Version from config
    debug=settings.debug,  # Debug mode
    lifespan=lifespan
)

# =========================================
# CROSS-ORIGIN RESOURCE SHARING (CORS) CONFIGURATION
# =========================================
# Configure CORS middleware to allow cross-origin requests from web browsers
# SECURITY NOTE: allow_origins=["*"] is permissive - restrict in production!

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# STATIC FILE SERVING CONFIGURATION
# =========================================
# Mount static directories to serve frontend assets, uploaded files, and resources
# These provide the web interface and supporting files for the application

app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")
app.mount("/tools/braking/assets", StaticFiles(directory="app/tools/braking/assets"), name="braking_assets")
app.mount("/tools/qmax/assets", StaticFiles(directory="app/tools/qmax/assets"), name="qmax_assets")
app.mount("/tools/hydraulic/assets", StaticFiles(directory="app/tools/hydraulic/assets"), name="hydraulic_assets")
app.mount("/tools/load_distribution/assets", StaticFiles(directory="app/tools/load_distribution/assets"), name="load_distribution_assets")
app.mount("/tools/tractive_effort/assets", StaticFiles(directory="app/tools/tractive_effort/assets"), name="tractive_effort_assets")
app.mount("/tools/vehicle_performance/assets", StaticFiles(directory="app/tools/vehicle_performance/assets"), name="vehicle_performance_assets")

# =============================
# API Routers Inclusion
# =============================
# Register all API routers for modular endpoints
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tools_router)
app.include_router(history_router)
app.include_router(admin_router)
app.include_router(messages_router)

# =============================
# HTML Page Routes
# =============================
# These routes serve HTML files for the frontend UI
from fastapi.responses import FileResponse


# Home page route
@app.get("/")
async def serve_home():
    """
    Serve the main application landing page (index.html).
    This is the default route for the web app UI.
    """
    return FileResponse("app/assets/html/index.html")

# Braking calculator page
@app.get("/braking_calculator.html")
async def serve_braking_calculator():
    """
    Serve the braking calculator tool page.
    Returns the HTML UI for braking calculations.
    """
    return FileResponse("app/tools/braking/assets/html/braking_calculator.html")

# Hydraulic calculator page
@app.get("/calculator.html")
async def serve_hydraulic_calculator():
    """
    Serve the hydraulic calculator tool page.
    Returns the HTML UI for hydraulic calculations.
    """
    return FileResponse("app/tools/hydraulic/assets/html/calculator.html")

# Qmax calculator page
@app.get("/qmax_calculator.html")
async def serve_qmax_calculator():
    """
    Serve the Qmax calculator tool page.
    Returns the HTML UI for Qmax calculations.
    """
    return FileResponse("app/tools/qmax/assets/html/qmax_calculator.html")

# Load distribution calculator page
@app.get("/load_distribution_calculator.html")
async def serve_load_distribution_calculator():
    """
    Serve the load distribution calculator tool page.
    Returns the HTML UI for load distribution calculations.
    """
    return FileResponse("app/tools/load_distribution/assets/html/load_distribution_calculator.html")


# Tractive effort calculator page
@app.get("/tractive_effort_calculator.html")
async def serve_tractive_effort_calculator():
    """
    Serve the tractive effort calculator tool page.
    Returns the HTML UI for tractive effort calculations.
    """
    return FileResponse("app/tools/tractive_effort/assets/html/tractive_effort_calculator.html")

# Vehicle performance calculator page
@app.get("/vehicle_performance_calculator.html")
async def serve_vehicle_performance_calculator():
    """
    Serve the vehicle performance calculator tool page.
    Returns the HTML UI for vehicle performance calculations.
    """
    return FileResponse("app/tools/vehicle_performance/assets/html/vehicle_performance_calculator.html")

# Login page
@app.get("/login.html")
async def serve_login():
    """
    Serve the login page for user authentication.
    """
    return FileResponse("app/assets/auth/login.html")

# Signup page
@app.get("/signup.html")
async def serve_signup():
    """
    Serve the signup page for new user registration.
    """
    return FileResponse("app/assets/auth/signup.html")

# Profile page
@app.get("/profile.html")
async def serve_profile():
    """
    Serve the user profile page.
    """
    return FileResponse("app/assets/auth/profile.html")

# Admin panel page
@app.get("/admin.html")
async def serve_admin():
    """
    Serve the admin panel page for admin users.
    """
    return FileResponse("app/assets/html/admin.html")

# Manager panel page
@app.get("/manager.html")
async def serve_manager():
    """
    Serve the manager panel page for manager users.
    """
    return FileResponse("app/assets/html/manager.html")

# =============================
# Static Pages (Legal, Support, Error)
# =============================

# Privacy policy page
@app.get("/privacy-policy.html")
async def serve_privacy_policy():
    """
    Serve the privacy policy page.
    """
    return FileResponse("app/assets/html/privacy-policy.html")


# Terms and conditions page
@app.get("/terms.html")
async def serve_terms():
    """
    Serve the terms and conditions page.
    """
    return FileResponse("app/assets/html/terms.html")

# Disclaimer page
@app.get("/disclaimer.html")
async def serve_disclaimer():
    """
    Serve the disclaimer page.
    """
    return FileResponse("app/assets/html/disclaimer.html")

# FAQ page
@app.get("/faq.html")
async def serve_faq():
    """
    Serve the frequently asked questions (FAQ) page.
    """
    return FileResponse("app/assets/html/faq.html")

# Documentation page
@app.get("/documentation.html")
async def serve_documentation():
    """
    Serve the documentation/help page.
    """
    return FileResponse("app/assets/html/documentation.html")

# 404 error page
@app.get("/404.html")
async def serve_404():
    """
    Serve the 404 (Not Found) error page.
    """
    return FileResponse("app/assets/html/404.html")

# 500 error page
@app.get("/500.html")
async def serve_500():
    """
    Serve the 500 (Internal Server Error) error page.
    """
    return FileResponse("app/assets/html/500.html")

# 403 error page
@app.get("/403.html")
async def serve_403():
    """
    Serve the 403 (Forbidden) error page.
    """
    return FileResponse("app/assets/html/403.html")


# =============================
# Main Entrypoint (for local run)
# =============================
if __name__ == "__main__":
    # Run the app with Uvicorn server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
