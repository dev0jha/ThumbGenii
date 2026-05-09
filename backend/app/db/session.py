"""
Database Session Management

SQLAlchemy engine and session configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.core.config import settings

# Create engine
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    from app.models.user import User
    from app.models.project import Project
    from app.models.generation import Generation
    from app.models.usage import Usage
    
    SQLModel.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session generator for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a database session directly."""
    return SessionLocal()
