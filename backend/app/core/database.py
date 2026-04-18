"""
Database engine & session factory.
Swap the engine/session setup for async (asyncpg) when you move to PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# -------------------------------------------------------------------------------
# Synchronous SQLite engine (great for development / small projects)
# For async PostgreSQL, replace with:
#   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
#   engine = create_async_engine(settings.DATABASE_URL, echo=True)
#   AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# -------------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only
    echo=settings.ENVIRONMENT == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -------------------------------------------------------------------------------
# Base model for all ORM models
# -------------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# -------------------------------------------------------------------------------
# Dependency — inject DB session into route handlers
# -------------------------------------------------------------------------------
def get_db():
    """Yield a database session and ensure it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
