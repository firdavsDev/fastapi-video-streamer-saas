from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_db
from app.services.video_service import (
    VideoAnalyticsService,
    VideoSearchService,
    VideoService,
)


# Dependency for video service
async def get_video_service(db: AsyncSession = Depends(get_async_db)) -> VideoService:
    return VideoService(db)


async def get_analytics_service(
    db: AsyncSession = Depends(get_async_db),
) -> VideoAnalyticsService:
    return VideoAnalyticsService(db)


async def get_search_service(
    db: AsyncSession = Depends(get_async_db),
) -> VideoSearchService:
    return VideoSearchService(db)


# Authentication dependency (simplified for now)
async def get_current_admin():
    """Simple admin authentication - replace with proper JWT validation"""
    return {"user_id": "admin", "username": "admin", "role": "admin"}
