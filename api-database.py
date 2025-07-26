from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
import os
import structlog

logger = structlog.get_logger()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://leave_admin:leave_pass@localhost:5432/leave_management")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis client
redis_client = None


async def get_redis():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


async def get_db_async():
    """Async database dependency"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Async database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()