"""Database connection and session management module utilizing SQLAlchemy 2.0.

Provides the database engine, session factory, declarative base for ORM models,
and session generator dependencies.
"""

from sqlalchemy import create_engine

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
