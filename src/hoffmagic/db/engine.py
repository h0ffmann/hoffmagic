"""
Database engine configuration for HoffMagic Blog.
"""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker, 
    create_async_engine
)
from sqlalchemy.orm import declarative_base

from hoffmagic.config import settings

# Initialize logger
logger = logging.getLogger("hoffmagic.db")

# Create SQLAlchemy base
Base = declarative_base()

# Create engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Initialize database connection and create tables if needed.
    """
    try:
        # Create tables - in production, use alembic instead
        if settings.ENV == "development":
            async with engine.begin() as conn:
                logger.info("Creating database tables")
                await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for dependency injection.
    
    Yields:
        A SQLAlchemy async session
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
