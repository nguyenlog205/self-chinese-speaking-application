from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.utils import load_config, create_logger

_config = load_config()
_db_config = _config.get("database", {})
_logger = create_logger("database_connection")

DATABASE_URL = _db_config.get("url", "sqlite+aiosqlite:///./default.db")

_logger.info(f"Initializing Async Database Engine with URL protocol: {DATABASE_URL.split('://')[0]}...")

engine = create_async_engine(DATABASE_URL, echo=False)

async_session_factory = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db_session():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            _logger.error(f"Database transaction failed, rolling back. Error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()