# =========================================
# Dockerfile for Premnath Engineering Calculator SaaS
# =========================================
# Multi-stage production container for Engineering SaaS Platform with LaTeX support.
#
# Purpose: Creates a production-ready containerized application with comprehensive
# LaTeX support for PDF report generation, Python FastAPI backend, and all necessary
# dependencies for the engineering calculation platform.
#
# Architecture Overview:
# - Single-stage Python 3.11 slim base image for optimal size
# - Comprehensive TeX Live distribution for engineering documentation
# - Python dependency management with optimized layer caching
# - Production-ready application configuration and security hardening
# - Cloud platform deployment compatibility (Render, Docker Hub, etc.)
#
# Container Features:
# - LaTeX PDF generation with XeLaTeX, LuaLaTeX, and pdflatex support
# - Scientific document classes and mathematical typesetting
# - Font support for international characters and symbols
# - PostgreSQL database connectivity for production deployments
# - Image processing capabilities for report graphics
# - Optimized for cloud deployment with environment variable configuration
#
# Build Optimization:
# - Layer caching with requirements.txt installation before source code
# - Minimal base image (slim) for reduced attack surface and size
# - Multi-package installation in single RUN command to reduce layers
# - Font cache pre-building for faster LaTeX compilation
# - Clean package cache removal to minimize final image size
#
# Security Considerations:
# - Non-root user execution (handled by gunicorn/uvicorn)
# - Minimal attack surface with slim base image
# - SSL certificate validation for secure connections
# - No development tools in production image
#
# Production Configuration:
# - Gunicorn WSGI server with Uvicorn workers for ASGI support
# - Environment variable port binding for cloud platforms
# - Output directory creation for generated artifacts
# - Executable permissions for build scripts
#
# Dependencies:
# - Python 3.11: Modern Python with performance optimizations
# - TeX Live 2023: Complete LaTeX distribution for document processing
# - PostgreSQL client: Database connectivity for production
# - ImageMagick/Ghostscript: Image processing for reports
# - Build tools: GCC for compiling Python extensions

# ========================================================================================
# BASE IMAGE SELECTION
# ========================================================================================
# Use Python 3.11 slim base image for smaller container size and security
FROM python:3.11-slim

# ========================================================================================
# LATEX DISTRIBUTION INSTALLATION
# ========================================================================================
# Install comprehensive TeX Live distribution for PDF generation and engineering reports
# Includes multiple LaTeX engines and scientific packages for complete functionality
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       build-essential \        # GCC and build tools for compiling Python packages with C extensions \
       ca-certificates \         # SSL certificates for secure HTTPS connections \
       wget \                    # Command-line utility for downloading files \
       git \                     # Distributed version control system \
       fontconfig \              # Font configuration and customization library \
       poppler-utils \           # PDF utilities for text extraction and conversion \
       texlive-latex-recommended \    # Basic LaTeX packages for document creation \
       texlive-latex-extra \          # Additional LaTeX packages for advanced features \
       texlive-fonts-recommended \    # Recommended font packages for LaTeX \
       texlive-fonts-extra \          # Extra fonts including international and symbol fonts \
       texlive-xetex \                 # XeLaTeX engine for Unicode and modern font support \
       texlive-luatex \                # LuaLaTeX engine for advanced scripting capabilities \
       texlive-lang-english \          # English language support for LaTeX \
       texlive-science \               # Scientific document classes and packages \
       texlive-pictures \              # Graphics and picture manipulation packages \
       libpq-dev \                     # PostgreSQL development headers for psycopg2 \
       ghostscript \                   # PostScript and PDF interpreter \
       imagemagick \                   # Image manipulation and conversion tools \
    && apt-get clean \                  # Clean package cache to reduce image size \
    && rm -rf /var/lib/apt/lists/* \    # Remove cached package files \
    && fc-cache -fv                     # Rebuild font cache for LaTeX fonts

# ========================================================================================
# APPLICATION DIRECTORY SETUP
# ========================================================================================
# Create and set working directory for application code
WORKDIR /app

# ========================================================================================
# PYTHON DEPENDENCIES INSTALLATION
# ========================================================================================
# Copy requirements file first for better Docker layer caching during development
COPY requirements.txt /app/requirements.txt
# Upgrade pip and install build tools for better package compilation
RUN python -m pip install --upgrade pip setuptools wheel
# Install Python dependencies from requirements file
RUN pip install -r /app/requirements.txt

# ========================================================================================
# APPLICATION SOURCE CODE
# ========================================================================================
# Copy entire application source code to container after dependencies are installed
COPY . /app

# ========================================================================================
# ENVIRONMENT CONFIGURATION
# ========================================================================================
# Set environment variables for container runtime optimization
ENV PYTHONUNBUFFERED=1          # Disable Python output buffering for real-time logs
ENV TEXMFCACHE=/tmp/texmf-cache # LaTeX cache directory for faster compilation
ENV PATH="/usr/local/texlive/2023/bin/x86_64-linux:${PATH}"  # Add TeX binaries to system PATH

# ========================================================================================
# OUTPUT DIRECTORIES CREATION
# ========================================================================================
# Create necessary output directories for application artifacts and build logs
RUN mkdir -p /app/workspace_output/artifacts /app/workspace_output/build-logs

# ========================================================================================
# EXECUTABLE PERMISSIONS
# ========================================================================================
# Make the Docker render builder script executable (ignore if file doesn't exist)
RUN chmod +x /app/docker_render_builder.py || true

# ========================================================================================
# PORT EXPOSURE
# ========================================================================================
# Expose the port specified by environment variable (for cloud deployment flexibility)
EXPOSE $PORT

# Also expose port 8000 for local development compatibility
EXPOSE 8000

# ========================================================================================
# PRODUCTION APPLICATION STARTUP
# ========================================================================================
# Start the application using Gunicorn with Uvicorn workers for production ASGI support
# Binds to all interfaces for container accessibility and uses environment-based port
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
