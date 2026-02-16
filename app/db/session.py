from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.logging import get_logger


engine = create_async_engine(
    settings.sqlalchemy_async_database_uri,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

logger = get_logger("db.session")


async def get_db() -> AsyncSession:
    db: AsyncSession = AsyncSessionLocal()
    logger.debug("DB async session opened")
    try:
        yield db
    finally:
        logger.debug("DB async session closed")
        await db.close()

