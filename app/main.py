"""
🎬 Video Streaming Backend - Main FastAPI Application
Entry point for the video streaming service
"""

import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.videos import router as videos_router
from app.core.config import settings
from app.core.database import health_check as db_health_check, init_database
from app.core.security import SecurityHeaders
from app.services.minio_service import MinIOService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Video Streaming Backend...")

    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("tmp", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

    # Initialize database
    db_success = await init_database()
    if not db_success:
        print("❌ Failed to initialize database")
        exit(1)

    # Initialize MinIO
    try:
        minio_service = MinIOService()
        health = await minio_service.health_check()
        if health["status"] == "healthy":
            print("✅ MinIO connection established")
        else:
            print(f"⚠️ MinIO connection issues: {health}")
    except Exception as e:
        print(f"❌ MinIO initialization failed: {e}")

    print("✅ Application startup complete")

    yield

    # Shutdown
    print("🔄 Shutting down Video Streaming Backend...")
    print("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="🎬 Secure video streaming backend with FastAPI, Celery, and MinIO",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Add security headers
    security_headers = SecurityHeaders.get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value

    return response


# CORS middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "Accept-Ranges"],
    )

# Trusted host middleware (production)
if settings.is_production:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    if settings.ENABLE_LOGGING:
        start_time = asyncio.get_event_loop().time()

        response = await call_next(request)

        process_time = asyncio.get_event_loop().time() - start_time
        print(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )

        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)

        return response
    else:
        return await call_next(request)


# Include routers
app.include_router(
    auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"]
)

app.include_router(
    videos_router, prefix=f"{settings.API_V1_STR}/videos", tags=["videos"]
)

# Static files (for frontend examples)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


# Health check endpoints
@app.get("/health")
async def health_check():
    """General health check"""
    try:
        # Check database
        db_health = await db_health_check()

        # Check MinIO
        minio_service = MinIOService()
        storage_health = await minio_service.health_check()

        # Overall status
        overall_status = (
            "healthy"
            if (
                db_health["status"] == "healthy"
                and storage_health["status"] == "healthy"
            )
            else "unhealthy"
        )

        return {
            "status": overall_status,
            "timestamp": asyncio.get_event_loop().time(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "services": {"database": db_health, "storage": storage_health},
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time(),
            },
        )


@app.get("/health/database")
async def database_health():
    """Database-specific health check"""
    return await db_health_check()


@app.get("/health/storage")
async def storage_health():
    """Storage-specific health check"""
    minio_service = MinIOService()
    return await minio_service.health_check()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"🎬 {settings.APP_NAME} v{settings.APP_VERSION}",
        "description": "Secure video streaming backend with FastAPI",
        "docs_url": (
            "/docs" if settings.DEBUG else "Documentation disabled in production"
        ),
        "health_check": "/health",
        "api_version": settings.API_V1_STR,
        "features": {
            "video_upload": True,
            "video_streaming": True,
            "thumbnail_generation": settings.ENABLE_VIDEO_THUMBNAILS,
            "analytics": settings.ENABLE_ANALYTICS,
            "video_resume": settings.ENABLE_VIDEO_RESUME,
        },
        "limits": {
            "max_upload_size_mb": settings.MAX_UPLOAD_SIZE // (1024 * 1024),
            "allowed_extensions": settings.ALLOWED_VIDEO_EXTENSIONS,
            "max_concurrent_uploads": settings.MAX_CONCURRENT_UPLOADS,
        },
    }


# API information
@app.get(f"{settings.API_V1_STR}/info")
async def api_info():
    """API information and capabilities"""
    return {
        "api_version": "v1",
        "endpoints": {
            "authentication": f"{settings.API_V1_STR}/auth/",
            "videos": f"{settings.API_V1_STR}/videos/",
            "health": "/health",
        },
        "upload_limits": {
            "max_file_size": settings.MAX_UPLOAD_SIZE,
            "allowed_types": settings.ALLOWED_VIDEO_EXTENSIONS,
            "max_concurrent": settings.MAX_CONCURRENT_UPLOADS,
        },
        "features": {
            "jwt_auth": True,
            "chunked_upload": True,
            "video_streaming": True,
            "progress_tracking": True,
            "thumbnail_generation": settings.ENABLE_VIDEO_THUMBNAILS,
            "analytics": settings.ENABLE_ANALYTICS,
            "search": settings.ENABLE_VIDEO_SEARCH,
        },
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource {request.url.path} was not found",
            "status_code": 404,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500,
        },
    )


# Rate limiting (if enabled)
if settings.RATE_LIMIT_ENABLED:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.AUTO_RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ENABLE_LOGGING,
    )
