"""Database connection and session management module utilizing SQLAlchemy 2.0.

Provides the database engine, session factory, declarative base for ORM models,
and session generator dependencies.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import settings
from src.logger import logger

# SQLAlchemy engine; SQLite needs check_same_thread=False
logger.info("Initializing SQLAlchemy database engine...")
is_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=True,
)

# Configure session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional scope around database operations.

    Yields a SQLAlchemy session and ensures automatic rollback on exception
    and reliable closure during teardown.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error encountered: {e}")
        db.rollback()
        raise
    finally:
        db.close()
