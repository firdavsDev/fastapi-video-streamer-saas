"""
🎬 Video Schemas - Pydantic Models for API
Data validation and serialization schemas for video operations
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# Base schemas
class VideoBase(BaseModel):
    """Base video schema with common fields"""

    title: str = Field(..., min_length=1, max_length=200, description="Video title")
    description: Optional[str] = Field(
        None, max_length=2000, description="Video description"
    )


class VideoCreate(VideoBase):
    """Schema for creating a new video"""

    tags: Optional[List[str]] = Field(default=[], description="Video tags")
    is_public: bool = Field(default=False, description="Whether video is public")
    is_featured: bool = Field(default=False, description="Whether video is featured")


class VideoUpdate(BaseModel):
    """Schema for updating video information"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None


class VideoResponse(BaseModel):
    """Schema for video response"""

    id: str
    title: str
    description: Optional[str] = None
    duration: Optional[float] = None
    file_size: int
    status: str
    thumbnail_path: Optional[str] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    uploaded_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    resolution: Optional[str] = None
    file_type: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False
    is_featured: bool = False

    class Config:
        from_attributes = True

    @validator("resolution", pre=True, always=True)
    def format_resolution(cls, v, values):
        """Format resolution from width and height"""
        if hasattr(values.get("width"), "__class__") and hasattr(
            values.get("height"), "__class__"
        ):
            width = getattr(values, "width", None)
            height = getattr(values, "height", None)
            if width and height:
                return f"{width}x{height}"
        return v or "Unknown"


class VideoListResponse(BaseModel):
    """Schema for paginated video list response"""

    videos: List[VideoResponse]
    total: int
    page: int
    per_page: int
    has_next: bool = False
    has_prev: bool = False

    @validator("has_next", pre=True, always=True)
    def calculate_has_next(cls, v, values):
        total = values.get("total", 0)
        page = values.get("page", 1)
        per_page = values.get("per_page", 10)
        return (page * per_page) < total

    @validator("has_prev", pre=True, always=True)
    def calculate_has_prev(cls, v, values):
        page = values.get("page", 1)
        return page > 1


class VideoUploadResponse(BaseModel):
    """Schema for video upload response"""

    video_id: str
    upload_session_id: str
    status: str
    message: str
    file_path: Optional[str] = None
    task_id: Optional[str] = None


class VideoUploadRequest(BaseModel):
    """Schema for video upload request"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = Field(default=[])
    is_public: bool = Field(default=False)
    is_featured: bool = Field(default=False)


# Progress tracking schemas
class VideoProgressRequest(BaseModel):
    """Schema for updating video progress"""

    current_time: float = Field(
        ..., ge=0, description="Current playback time in seconds"
    )
    session_id: str = Field(..., min_length=1, description="User session ID")
    user_id: Optional[str] = Field(None, description="User ID (optional)")


class VideoProgressResponse(BaseModel):
    """Schema for video progress response"""

    video_id: str
    current_time: float
    completion_percentage: float
    resume_position: float
    last_accessed: datetime
    is_completed: bool = False


# Analytics schemas
class VideoStatsResponse(BaseModel):
    """Schema for video statistics"""

    video_id: str
    total_views: int
    unique_viewers: int
    total_watch_time: float
    average_watch_time: float
    completion_rate: float
    file_size_mb: float
    duration: Optional[float] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class VideoAnalyticsResponse(BaseModel):
    """Schema for detailed video analytics"""

    video_id: str
    video_title: str
    period: Dict[str, Optional[str]]
    metrics: Dict[str, float]
    video_info: Dict[str, Any]


class TopVideosResponse(BaseModel):
    """Schema for top videos response"""

    videos: List[Dict[str, Any]]
    period_days: int
    metric: str
    generated_at: datetime


# Search schemas
class VideoSearchRequest(BaseModel):
    """Schema for video search request"""

    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    filters: Optional[Dict[str, Any]] = Field(default={})


class VideoSearchResponse(BaseModel):
    """Schema for video search response"""

    query: str
    results: List[VideoResponse]
    total: int
    offset: int
    limit: int
    filters: Dict[str, Any]


class VideoRecommendationsResponse(BaseModel):
    """Schema for video recommendations"""

    video_id: str
    recommendations: List[VideoResponse]
    algorithm: str = "similarity"
    generated_at: datetime


# Status and info schemas
class VideoStatusResponse(BaseModel):
    """Schema for video status response"""

    video_id: str
    status: str
    processing_progress: int = Field(ge=0, le=100)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    uploaded_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class VideoUrlResponse(BaseModel):
    """Schema for video URL response"""

    video_id: str
    video_url: str
    expires_in: int
    expires_at: datetime
    access_type: str = "streaming"


# Batch operation schemas
class BatchDeleteRequest(BaseModel):
    """Schema for batch delete request"""

    video_ids: List[str] = Field(..., min_items=1, max_items=50)
    confirm: bool = Field(default=False, description="Confirmation flag")


class BatchDeleteResponse(BaseModel):
    """Schema for batch delete response"""

    results: List[Dict[str, Any]]
    total_requested: int
    successful: int
    failed: int
    errors: List[str] = []


class BatchUpdateRequest(BaseModel):
    """Schema for batch update request"""

    video_ids: List[str] = Field(..., min_items=1, max_items=50)
    updates: Dict[str, Any] = Field(..., description="Fields to update")


# Dashboard schemas
class DashboardOverviewResponse(BaseModel):
    """Schema for dashboard overview"""

    summary: Dict[str, Any]
    # top_videos: List[Dict[str, Any]]
    recent_uploads: List[VideoResponse]
    analytics: Dict[str, Any]
    period: str
    generated_at: datetime


class SystemStatsResponse(BaseModel):
    """Schema for system statistics"""

    total_videos: int
    total_storage_mb: float
    total_views: int
    total_watch_time_hours: float
    active_users: int
    upload_rate_24h: int
    processing_queue: int
    storage_usage: Dict[str, Any]
    performance_metrics: Dict[str, Any]


# Error schemas
class ErrorResponse(BaseModel):
    """Schema for error responses"""

    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""

    error: str = "Validation Error"
    message: str
    status_code: int = 422
    validation_errors: List[Dict[str, Any]]
    timestamp: datetime


# Success schemas
class SuccessResponse(BaseModel):
    """Schema for success responses"""

    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


# Health check schemas
class HealthCheckResponse(BaseModel):
    """Schema for health check response"""

    status: str
    timestamp: float
    version: str
    environment: str
    services: Dict[str, Dict[str, Any]]


class ServiceHealthResponse(BaseModel):
    """Schema for individual service health"""

    status: str
    service: str
    response_time_ms: Optional[float] = None
    details: Dict[str, Any]
    last_check: datetime


# API Info schemas
class APIInfoResponse(BaseModel):
    """Schema for API information"""

    api_version: str
    endpoints: Dict[str, str]
    upload_limits: Dict[str, Any]
    features: Dict[str, bool]
    rate_limits: Dict[str, Any]
    documentation_url: str
