from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base

SQLALCHEMY_DATABASE_URL = settings.database_url

connect_args = (
    {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=settings.debug,  # Enable query logging in debug mode
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency function to get database session"""
    async with SessionLocal() as db:
        yield db
