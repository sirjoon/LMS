from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
import os
import traceback
from contextlib import asynccontextmanager

from database import engine, Base, get_redis
from models import *
from routers import auth, admin, manager, employee, shared
from seed import seed_demo_data
from utils.logging_config import setup_logging


# Setup structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Leave Management System API")
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Seed demo data if enabled
        if os.getenv("SEED_DEMO", "").lower() == "true":
            await seed_demo_data()
            logger.info("Demo data seeded successfully")
            
        # Test Redis connection
        redis_client = await get_redis()
        await redis_client.ping()
        logger.info("Redis connection established")
        
    except Exception as e:
        logger.error("Startup failed", error=str(e), traceback=traceback.format_exc())
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Leave Management System API")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Leave Management System",
    description="A comprehensive leave management system for corporate use",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware (can be disabled for testing)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        traceback=traceback.format_exc()
    )
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_type": "http_exception"}
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": "internal_error"
        }
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s"
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            process_time=f"{process_time:.3f}s"
        )
        raise


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Check Redis connection
        redis_client = await get_redis()
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(manager.router, prefix="/manager", tags=["manager"])
app.include_router(employee.router, prefix="/employee", tags=["employee"])
app.include_router(shared.router, tags=["shared"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Leave Management System API",
        "version": "1.0.0",
        "status": "running"
    }