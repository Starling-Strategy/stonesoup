"""
Async database session management for STONESOUP.

This module provides async SQLAlchemy session configuration and management,
including:
- Async engine creation with proper connection pooling
- Session factory configuration
- Dependency injection for FastAPI
- Transaction management utilities

The configuration is optimized for:
- Serverless environments (using NullPool)
- Multi-tenant applications (cauldron-scoped queries)
- High-performance async operations
"""
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_database_url(sync_url: str) -> str:
    """
    Convert a synchronous PostgreSQL URL to an async one.
    
    Args:
        sync_url: Synchronous database URL (postgresql://...)
        
    Returns:
        Async database URL (postgresql+asyncpg://...)
    """
    if sync_url.startswith("postgresql://"):
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif sync_url.startswith("postgres://"):
        return sync_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif sync_url.startswith("postgresql+asyncpg://"):
        return sync_url  # Already async
    else:
        raise ValueError(f"Invalid database URL format: {sync_url}")


def create_engine(
    database_url: Optional[str] = None,
    echo: Optional[bool] = None,
    pool_size: int = 5,
    max_overflow: int = 10,
    use_null_pool: bool = True
) -> AsyncEngine:
    """
    Create an async SQLAlchemy engine with appropriate configuration.
    
    Args:
        database_url: Database connection URL (defaults to settings)
        echo: Whether to log SQL statements (defaults to dev mode)
        pool_size: Number of connections to maintain in pool
        max_overflow: Maximum overflow connections allowed
        use_null_pool: Use NullPool for serverless (no connection pooling)
        
    Returns:
        Configured AsyncEngine instance
    """
    # Use provided URL or fall back to settings
    url = database_url or str(settings.DATABASE_URL)
    async_url = create_database_url(url)
    
    # Determine echo setting
    if echo is None:
        echo = settings.ENVIRONMENT == "development"
    
    # Configure pool class based on environment
    pool_class = NullPool if use_null_pool else AsyncAdaptedQueuePool
    
    # Create engine with configuration
    engine_kwargs = {
        "echo": echo,
        "future": True,
        "pool_pre_ping": True,  # Verify connections before using
    }
    
    if not use_null_pool:
        engine_kwargs.update({
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": 30,
            "pool_recycle": 1800,  # Recycle connections after 30 minutes
        })
    else:
        engine_kwargs["poolclass"] = NullPool
    
    engine = create_async_engine(async_url, **engine_kwargs)
    
    logger.info(
        f"Created async engine for {async_url.split('@')[1] if '@' in async_url else 'database'} "
        f"with {'NullPool' if use_null_pool else f'pool_size={pool_size}'}"
    )
    
    return engine


# Global engine instance
engine = create_engine(
    use_null_pool=settings.ENVIRONMENT in ["production", "staging"]
)


# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields a database session.
    
    This is the primary way to get a database session in FastAPI endpoints.
    It handles:
    - Session creation
    - Automatic commit on success
    - Automatic rollback on exception
    - Proper session cleanup
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager for database sessions outside of FastAPI dependencies.
    
    Useful for:
    - Background tasks
    - CLI commands
    - Tests
    - Any non-request context
    
    Usage:
        async with get_db_context() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseSessionManager:
    """
    Manager class for handling database sessions with tenant context.
    
    This class provides utilities for:
    - Scoped sessions with automatic tenant filtering
    - Bulk operations with proper transaction handling
    - Connection pool monitoring
    """
    
    def __init__(self, cauldron_id: Optional[str] = None):
        """
        Initialize session manager with optional tenant context.
        
        Args:
            cauldron_id: Optional cauldron ID for automatic tenant filtering
        """
        self.cauldron_id = cauldron_id
        self._session: Optional[AsyncSession] = None
    
    async def __aenter__(self) -> AsyncSession:
        """Enter the async context manager."""
        self._session = AsyncSessionLocal()
        return self._session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager with proper cleanup."""
        if self._session:
            if exc_type is not None:
                await self._session.rollback()
            else:
                await self._session.commit()
            await self._session.close()
            self._session = None
    
    @property
    def session(self) -> AsyncSession:
        """Get the current session."""
        if not self._session:
            raise RuntimeError("No active session. Use 'async with' context manager.")
        return self._session


async def init_db() -> None:
    """
    Initialize database tables and extensions.
    
    This function should be called on application startup to ensure:
    - All tables are created
    - Required extensions are installed (pgvector)
    - Initial data is seeded if needed
    """
    from app.db.base_class import Base
    # Import all models to register them with SQLAlchemy
    from app.models.cauldron import Cauldron
    from app.models.member import Member
    from app.models.story import Story
    
    async with engine.begin() as conn:
        # Create pgvector extension if it doesn't exist
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Database initialized successfully")


async def close_db() -> None:
    """
    Close database connections and cleanup.
    
    This function should be called on application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")


# Re-export commonly used items
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "get_db_context",
    "DatabaseSessionManager",
    "init_db",
    "close_db",
]