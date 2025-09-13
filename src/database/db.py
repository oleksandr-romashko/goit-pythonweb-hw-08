"""
Database session management.

Defines an async SQLAlchemy engine and session manager for use
throughout the application. Provides a FastAPI dependency for
database sessions.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.config.app_config import config


class DatabaseSessionManager:
    """Manages an async SQLAlchemy engine and session maker."""

    def __init__(self, url: str):
        """Initialize the engine and session maker with the given database URL."""
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """Provide an async context manager for a database session."""
        if self._session_maker is None:
            raise RuntimeError("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


session_manager = DatabaseSessionManager(config.DB_URL)
"""Singleton instance of DatabaseSessionManager with configured DB URL."""


async def get_db():
    """FastAPI dependency to provide an async database session."""
    async with session_manager.session() as session:
        yield session
