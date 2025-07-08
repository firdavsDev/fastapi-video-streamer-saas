"""
🎬 Video Streaming Backend Database Configuration
SQLAlchemy setup with async support
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import text

from app.core.config import settings

# 🗄️ Database Configuration
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
SQLALCHEMY_DATABASE_URL_ASYNC = settings.database_url_async

# 🔧 Engine Configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL_ASYNC,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
else:
    print("Using PostgreSQL database configuration", SQLALCHEMY_DATABASE_URL)
    print(
        "Using PostgreSQL async database configuration", SQLALCHEMY_DATABASE_URL_ASYNC
    )
    # PostgreSQL configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
    )

    async_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL_ASYNC,
        echo=False,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
    )

# 🏗️ Session Configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# 📋 Base Model
Base = declarative_base()

# 🔧 Metadata for migrations
metadata = MetaData()


# 🔄 Database Dependencies
def get_db():
    """
    Dependency to get database session (sync)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 🚀 Database Utilities
class DatabaseManager:
    """Database management utilities"""

    @staticmethod
    async def create_tables():
        """Create all database tables"""
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            raise e

    @staticmethod
    async def drop_tables():
        """Drop all database tables"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def reset_database():
        """Reset database (drop and create tables)"""
        await DatabaseManager.drop_tables()
        await DatabaseManager.create_tables()

    @staticmethod
    async def check_connection() -> bool:
        """Check if database connection is working"""
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    @staticmethod
    def create_tables_sync():
        """Create tables synchronously (for development)"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def drop_tables_sync():
        """Drop tables synchronously (for development)"""
        Base.metadata.drop_all(bind=engine)


# 🎯 Database Initialization
async def init_database():
    """Initialize database on startup"""
    try:
        # Check connection
        connection_ok = await DatabaseManager.check_connection()
        if not connection_ok:
            raise Exception("Database connection failed")

        # Create tables if they don't exist
        await DatabaseManager.create_tables()

        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


# 🔧 Database Session Context
class DatabaseSession:
    """Database session context manager"""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self._should_close = session is None

    async def __aenter__(self) -> AsyncSession:
        if self.session is None:
            self.session = AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._should_close and self.session:
            await self.session.close()

    async def commit(self):
        """Commit the transaction"""
        if self.session:
            await self.session.commit()

    async def rollback(self):
        """Rollback the transaction"""
        if self.session:
            await self.session.rollback()


# 🎲 Database Testing Utilities
class TestDatabase:
    """Database utilities for testing"""

    @staticmethod
    async def setup_test_db():
        """Setup test database"""
        await DatabaseManager.create_tables()

    @staticmethod
    async def cleanup_test_db():
        """Cleanup test database"""
        await DatabaseManager.drop_tables()

    @staticmethod
    async def reset_test_db():
        """Reset test database"""
        await DatabaseManager.reset_database()


# 🔍 Database Health Check
async def health_check() -> dict:
    """Database health check"""
    try:
        start_time = asyncio.get_event_loop().time()

        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()

        end_time = asyncio.get_event_loop().time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "engine": str(async_engine.url).split("://")[0],
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "engine": str(async_engine.url).split("://")[0],
        }


# 📊 Database Statistics
async def get_database_stats() -> dict:
    """Get database statistics"""
    try:
        async with AsyncSessionLocal() as session:
            # Get table information
            if settings.DATABASE_URL.startswith("sqlite"):
                result = await session.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in result.fetchall()]
            else:
                result = await session.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                )
                tables = [row[0] for row in result.fetchall()]

            return {
                "tables": tables,
                "table_count": len(tables),
                "database_url": settings.DATABASE_URL.split("://")[0] + "://***",
                "pool_size": (
                    async_engine.pool.size()
                    if hasattr(async_engine.pool, "size")
                    else "N/A"
                ),
            }
    except Exception as e:
        return {
            "error": str(e),
            "database_url": settings.DATABASE_URL.split("://")[0] + "://***",
        }
