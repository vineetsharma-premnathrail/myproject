
"""
Database Session Management Module
---------------------------------
Purpose:
    Configures SQLAlchemy engine, session, and base for database operations.
    Provides dependency injection for database sessions in FastAPI endpoints.
Layer:
    Backend / Database / Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Generator
from app.config import settings

# Database engine configuration (supports SQLite and other DBs)
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Session factory for creating new DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to provide a database session.

    Yields:
        Session: SQLAlchemy session object

    Ensures the session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables defined in ORM models.

    Returns:
        None
    """
    Base.metadata.create_all(bind=engine)

def reset_database():
    """
    Drop and recreate all tables (for development/testing only).

    Returns:
        None
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)