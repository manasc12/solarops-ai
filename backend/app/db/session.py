"""SQLite database configuration and session management.

Provides thread-safe database connections and ORM session factory.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = Path("data/solarops.db")
DB_URL = f"sqlite:///{DB_PATH.absolute()}"

# Create data directory if it doesn't exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLAlchemy base for ORM models
Base = declarative_base()

# Database engine
_engine = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            DB_URL,
            connect_args={"check_same_thread": False},  # SQLite allows this in single-process
            echo=False,  # Set to True for SQL query logging
        )
        logger.info(f"Database engine created: {DB_URL}")
    return _engine


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine(),
)


def get_session() -> Session:
    """Get a new database session."""
    return SessionLocal()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables initialized")
