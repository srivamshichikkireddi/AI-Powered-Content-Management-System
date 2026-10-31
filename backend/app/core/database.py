import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


# Ensure URL uses asyncpg for PostgreSQL
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_health() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False
