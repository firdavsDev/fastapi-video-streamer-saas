"""
🎬 Video Streaming Backend Models
Database models for video management
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class VideoStatus(str, Enum):
    """Video processing status"""

    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class VideoQuality(str, Enum):
    """Video quality options"""

    QUALITY_240P = "240p"
    QUALITY_360P = "360p"
    QUALITY_480P = "480p"
    QUALITY_720P = "720p"
    QUALITY_1080P = "1080p"
    QUALITY_1440P = "1440p"
    QUALITY_2160P = "2160p"


class Video(Base):
    """Video model for storing video metadata and information"""

    __tablename__ = "videos"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic video information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)

    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), nullable=False)
    file_extension = Column(String(10), nullable=False)

    # Video metadata
    duration = Column(Float, nullable=True)  # in seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    bitrate = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)

    # Processing status
    status = Column(String(20), nullable=False, default=VideoStatus.PENDING)
    processing_progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)

    # Thumbnail information
    thumbnail_path = Column(String(500), nullable=True)
    thumbnail_generated = Column(Boolean, default=False)

    # Access control
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)

    # Metadata and tags
    tags = Column(JSON, nullable=True)
    # metadata = Column(JSON, nullable=True)

    # Quality versions
    available_qualities = Column(
        JSON, nullable=True
    )  # List of available quality versions

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    upload_sessions = relationship(
        "VideoUploadSession", back_populates="video", cascade="all, delete-orphan"
    )
    view_sessions = relationship(
        "VideoViewSession", back_populates="video", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Video(id={self.id}, title={self.title}, status={self.status})>"

    @property
    def is_processing(self) -> bool:
        """Check if video is currently being processed"""
        return self.status in [
            VideoStatus.PENDING,
            VideoStatus.UPLOADING,
            VideoStatus.PROCESSING,
        ]

    @property
    def is_ready(self) -> bool:
        """Check if video is ready for streaming"""
        return self.status == VideoStatus.COMPLETED

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (HH:MM:SS)"""
        if not self.duration:
            return "00:00:00"

        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def resolution(self) -> str:
        """Get video resolution"""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Unknown"


class VideoUploadSession(Base):
    """Video upload session for tracking upload progress"""

    __tablename__ = "video_upload_sessions"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to video
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)

    # Upload information
    session_token = Column(String(255), nullable=False, unique=True)
    upload_url = Column(String(500), nullable=True)
    chunk_size = Column(Integer, nullable=False, default=8192)
    total_chunks = Column(Integer, nullable=True)
    uploaded_chunks = Column(Integer, default=0)

    # Progress tracking
    bytes_uploaded = Column(Integer, default=0)
    upload_progress = Column(Float, default=0.0)  # 0.0 - 100.0
    upload_speed = Column(Float, nullable=True)  # bytes per second

    # Status
    status = Column(String(20), nullable=False, default=VideoStatus.PENDING)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    video = relationship("Video", back_populates="upload_sessions")

    def __repr__(self):
        return f"<VideoUploadSession(id={self.id}, video_id={self.video_id}, progress={self.upload_progress}%)>"

    @property
    def is_active(self) -> bool:
        """Check if upload session is active"""
        return self.status in [VideoStatus.PENDING, VideoStatus.UPLOADING]

    @property
    def is_completed(self) -> bool:
        """Check if upload is completed"""
        return self.status == VideoStatus.COMPLETED

    @property
    def estimated_time_remaining(self) -> Optional[float]:
        """Estimate time remaining for upload (in seconds)"""
        if not self.upload_speed or self.upload_progress >= 100:
            return None

        bytes_remaining = (
            self.video.file_size if self.video else 0
        ) - self.bytes_uploaded
        if bytes_remaining <= 0:
            return 0

        return bytes_remaining / self.upload_speed


class VideoViewSession(Base):
    """Video view session for tracking user viewing progress"""

    __tablename__ = "video_view_sessions"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to video
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)

    # User information (optional for anonymous viewing)
    user_id = Column(String, nullable=True)
    session_id = Column(String(255), nullable=False)  # Browser session or user session
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Viewing progress
    current_time = Column(Float, default=0.0)  # Current playback position in seconds
    watch_duration = Column(Float, default=0.0)  # Total time spent watching
    completion_percentage = Column(Float, default=0.0)  # Percentage of video watched

    # Playback information
    last_quality = Column(String(10), nullable=True)  # Last selected quality
    playback_speed = Column(Float, default=1.0)
    volume_level = Column(Float, default=1.0)

    # Session status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    paused_at = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="view_sessions")

    def __repr__(self):
        return f"<VideoViewSession(id={self.id}, video_id={self.video_id}, progress={self.completion_percentage}%)>"

    @property
    def resume_position(self) -> float:
        """Get position where user should resume watching"""
        return self.current_time

    @property
    def has_finished(self) -> bool:
        """Check if user has finished watching the video"""
        return self.completion_percentage >= 95.0  # Consider 95% as "finished"

    def update_progress(self, current_time: float, video_duration: float):
        """Update viewing progress"""
        self.current_time = current_time
        self.completion_percentage = (
            (current_time / video_duration) * 100 if video_duration > 0 else 0
        )
        self.last_accessed = datetime.utcnow()

        if self.completion_percentage >= 95.0:
            self.is_completed = True


class VideoAnalytics(Base):
    """Video analytics for tracking performance and usage"""

    __tablename__ = "video_analytics"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to video
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)

    # Analytics data
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    views_count = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    total_watch_time = Column(Float, default=0.0)  # in seconds
    average_watch_time = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)  # percentage

    # Engagement metrics
    likes_count = Column(Integer, default=0)
    dislikes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)

    # Quality metrics
    buffer_events = Column(Integer, default=0)
    error_events = Column(Integer, default=0)
    quality_switches = Column(Integer, default=0)

    # Geographic data
    country_stats = Column(JSON, nullable=True)
    device_stats = Column(JSON, nullable=True)
    browser_stats = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<VideoAnalytics(id={self.id}, video_id={self.video_id}, views={self.views_count})>"
