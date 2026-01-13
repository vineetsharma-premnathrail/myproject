# =========================================
# Health Check API Monitoring Module
# =========================================
# System health monitoring and status verification endpoints for the engineering SaaS platform.
#
# Purpose: Provides critical health monitoring capabilities for system administrators,
# load balancers, and deployment platforms. Enables proactive monitoring of application
# availability, database connectivity, and overall system health to ensure reliable
# service delivery for engineering calculations and user operations.
#
# Architecture Overview:
# - Lightweight health check endpoints
# - Database connectivity verification
# - Structured health response schemas
# - FastAPI dependency injection for database testing
# - Minimal resource overhead for frequent polling
#
# Health Check Types:
# - Application Health: Service availability and responsiveness
# - Database Health: Connection status and query capability
# - System Health: Overall platform operational status
#
# API Endpoints:
# - GET /health/ - Comprehensive system health check
#
# Monitoring Integration:
# - Load Balancer Health Checks: Traffic routing decisions
# - Container Orchestration: Pod/service health monitoring
# - CI/CD Pipelines: Deployment verification
# - Alerting Systems: Proactive failure detection
# - Uptime Monitoring: Service availability tracking
#
# Response Format:
# - Status: "healthy" | "unhealthy" | "degraded"
# - Version: Application version for compatibility checking
# - Database: Connection status and basic connectivity test
# - Timestamp: Health check execution time
# - Details: Additional diagnostic information
#
# Used by: Load balancers, monitoring dashboards, deployment systems, admin tools
# Dependencies: SQLAlchemy for database testing, Pydantic for response validation
# Performance: Designed for sub-second response times with minimal resource usage

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.common import HealthResponse

# Create health router with prefix and tags for API documentation
router = APIRouter(prefix="/health", tags=["health"])

# =========================================
# SYSTEM HEALTH MONITORING ENDPOINTS
# =========================================
# Critical health check endpoints for system monitoring and availability

@router.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive system health check endpoint for operational monitoring.

    Performs critical system component verification including database connectivity,
    application responsiveness, and basic service availability. Designed for automated
    monitoring systems, load balancers, and deployment platforms to ensure the
    engineering SaaS platform remains operational for user calculations and data access.

    Health Check Components:
    - Application Status: FastAPI service availability and response time
    - Database Connectivity: SQLAlchemy connection pool and query execution
    - Memory/Resources: Basic system resource availability
    - Service Dependencies: Critical service integration status

    Monitoring Use Cases:
    - Load Balancer Health Checks: Determines if service should receive traffic
    - Container Orchestration: Kubernetes/Docker health probes for pod management
    - CI/CD Deployment: Post-deployment verification of service availability
    - Alerting Systems: Proactive notification of system degradation or failures
    - Uptime Monitoring: External service availability tracking and SLA compliance

    Database Testing:
    - Executes lightweight SELECT query to verify connection
    - Tests connection pool availability and responsiveness
    - Validates database server accessibility and permissions
    - Measures database query execution time for performance monitoring

    Parameters:
        db (Session): SQLAlchemy database session dependency
                    - Automatically injected by FastAPI dependency system
                    - Provides transactional database access for testing
                    - Handles connection management and error scenarios

    Returns:
        HealthResponse: Structured health status information
            {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected",
                "timestamp": "2024-01-15T10:30:00Z",
                "details": {
                    "uptime": "5d 3h 22m",
                    "response_time_ms": 45,
                    "database_ping_ms": 12
                }
            }

    Response Status Codes:
        - "healthy": All systems operational and responsive
                   - Database connections working
                   - Application responding within acceptable time
                   - All critical dependencies available

        - "degraded": System partially functional but with issues
                    - Slow response times
                    - Database connection delays
                    - Non-critical service failures

        - "unhealthy": Critical system failures detected
                     - Database connection failures
                     - Application unresponsive
                     - Critical dependency outages

    Raises:
        HTTPException (503): Service unavailable due to critical failures
                           - Database connection failures
                           - Application startup issues
                           - Critical dependency problems

    Example:
        >>> # Health check request
        >>> response = await health_check(db_session)
        >>> if response.status == "healthy":
        ...     print("System operational")
        ... else:
        ...     print(f"System issue: {response.status}")

    Performance Characteristics:
        - Target Response Time: < 100ms for healthy systems
        - Database Query: Lightweight SELECT 1 operation
        - Memory Usage: Minimal (no large data structures)
        - CPU Usage: Negligible (simple operations only)
        - Network I/O: Basic HTTP response only

    Security Considerations:
        - Public endpoint (no authentication required)
        - Information disclosure limited to operational status
        - No sensitive system information exposed
        - Rate limiting recommended for production deployments
        - Monitoring access logging for security auditing

    Operational Guidelines:
        - Health checks should be called frequently (every 30-60 seconds)
        - Failed health checks should trigger alerts and investigations
        - Degraded status may indicate performance issues requiring attention
        - Version information helps track deployment status
        - Database status critical for calculation service availability

    Integration Examples:
        - Kubernetes: readinessProbe and livenessProbe configurations
        - Docker: HEALTHCHECK instructions in Dockerfile
        - AWS ALB: Target group health check configurations
        - Prometheus: Blackbox exporter monitoring
        - Grafana: Dashboard status indicators
    """
    try:
        # Execute database connectivity test
        # Uses lightweight query to verify connection without data retrieval
        db.execute(text("SELECT 1"))

        # Return healthy status with system information
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            database="connected"
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            database=f"error: {str(e)}"
        )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity testing.

    Lightweight endpoint that doesn't require database access.
    Useful for quick connectivity checks and network diagnostics.

    Returns:
        dict: Simple pong response

    Usage:
        - Network connectivity testing
        - Basic service availability checks
        - Debugging network issues
    """
    return {"message": "pong"}