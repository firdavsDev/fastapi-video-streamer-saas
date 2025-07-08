"""
🎬 Video Service - Business Logic Layer
Handles video operations, processing, and management
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import cv2
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.security import SecurityManager
from app.models.video import Video, VideoStatus, VideoUploadSession, VideoViewSession
from app.services.minio_service import MinIOService


class VideoService:
    """Video service for managing video operations"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.minio_service = MinIOService()
        self.security = SecurityManager()

    async def create_video(
        self,
        title: str,
        description: Optional[str] = None,
        file: Optional[UploadFile] = None,
        **kwargs,
    ) -> Video:
        """Create a new video record"""

        # Generate unique video ID
        video_id = str(uuid.uuid4())

        # Prepare video data
        video_data = {
            "id": video_id,
            "title": title,
            "description": description,
            "status": VideoStatus.PENDING,
            "created_at": datetime.utcnow(),
            **kwargs,
        }

        # If file is provided, process it
        if file:
            # Validate file
            await self._validate_video_file(file)

            # Generate secure filename
            secure_filename = self.security.generate_secure_filename(file.filename)

            # Update video data with file information
            video_data.update(
                {
                    "filename": secure_filename,
                    "original_filename": file.filename,
                    "file_size": file.size,
                    "file_type": file.content_type,
                    "file_extension": os.path.splitext(file.filename)[1].lower(),
                    "file_path": f"videos/{video_id}/{secure_filename}",
                }
            )

        # Create video record
        video = Video(**video_data)
        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)

        return video

    async def get_video_by_id(self, video_id: str) -> Optional[Video]:
        """Get video by ID"""
        result = await self.db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()

    async def get_videos(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VideoStatus] = None,
        search: Optional[str] = None,
    ) -> List[Video]:
        """Get list of videos with filtering"""
        query = select(Video)

        # Apply filters
        if status:
            query = query.where(Video.status == status)

        if search:
            query = query.where(Video.title.ilike(f"%{search}%"))

        # Apply pagination and ordering
        query = query.order_by(Video.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def upload_video_file(
        self, video: Video, file: UploadFile, chunk_size: int = 8192
    ) -> VideoUploadSession:
        """Upload video file to storage"""

        # Create upload session
        upload_session = VideoUploadSession(
            id=str(uuid.uuid4()),
            video_id=video.id,
            session_token=str(uuid.uuid4()),
            chunk_size=chunk_size,
            status=VideoStatus.UPLOADING,
            started_at=datetime.utcnow(),
        )

        self.db.add(upload_session)
        await self.db.commit()

        try:
            # Update video status
            video.status = VideoStatus.UPLOADING
            await self.db.commit()

            # Upload file to MinIO
            file_path = f"videos/{video.id}/{video.filename}"

            # Read file content
            file_content = await file.read()
            upload_session.bytes_uploaded = len(file_content)

            # Upload to storage
            await self.minio_service.upload_file(
                file_path, file_content, content_type=video.file_type
            )

            # Update upload session
            upload_session.status = VideoStatus.COMPLETED
            upload_session.upload_progress = 100.0
            upload_session.completed_at = datetime.utcnow()

            # Update video
            video.status = VideoStatus.PROCESSING
            video.file_path = file_path
            video.uploaded_at = datetime.utcnow()

            await self.db.commit()

            # Trigger background processing
            await self._process_video_metadata(video)

            return upload_session

        except Exception as e:
            # Update status on error
            upload_session.status = VideoStatus.FAILED
            upload_session.error_message = str(e)
            video.status = VideoStatus.FAILED
            video.error_message = str(e)

            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {str(e)}",
            )

    async def delete_video(self, video_id: str) -> bool:
        """Delete video and associated files"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        try:
            # Delete file from storage
            if video.file_path:
                await self.minio_service.delete_file(video.file_path)

            # Delete thumbnail if exists
            if video.thumbnail_path:
                await self.minio_service.delete_file(video.thumbnail_path)

            # Mark as deleted
            video.status = VideoStatus.DELETED
            await self.db.commit()

            return True

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete video: {str(e)}",
            )

    async def get_video_stream_url(
        self, video_id: str, quality: Optional[str] = None, expires_in: int = 3600
    ) -> str:
        """Get presigned URL for video streaming"""
        video = await self.get_video_by_id(video_id)
        if not video or video.status != VideoStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found or not ready",
            )

        # Generate presigned URL
        presigned_url = await self.minio_service.get_presigned_url(
            video.file_path, expires_in=expires_in
        )

        return presigned_url

    async def stream_video_content(self, video_id: str) -> bytes:
        """Get video content for streaming"""
        video = await self.get_video_by_id(video_id)
        if not video or video.status != VideoStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found or not ready",
            )

        # Get file content from storage
        content = await self.minio_service.get_file_content(video.file_path)
        return content

    async def update_video_progress(
        self,
        video_id: str,
        session_id: str,
        current_time: float,
        user_id: Optional[str] = None,
    ) -> VideoViewSession:
        """Update video viewing progress"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        # Find or create view session
        result = await self.db.execute(
            select(VideoViewSession).where(
                VideoViewSession.video_id == video_id,
                VideoViewSession.session_id == session_id,
            )
        )
        view_session = result.scalar_one_or_none()

        if not view_session:
            view_session = VideoViewSession(
                id=str(uuid.uuid4()),
                video_id=video_id,
                session_id=session_id,
                user_id=user_id,
            )
            self.db.add(view_session)

        # Update progress
        if video.duration:
            view_session.update_progress(current_time, video.duration)

        await self.db.commit()
        return view_session

    async def get_video_progress(
        self, video_id: str, session_id: str
    ) -> Optional[VideoViewSession]:
        """Get video viewing progress"""
        result = await self.db.execute(
            select(VideoViewSession).where(
                VideoViewSession.video_id == video_id,
                VideoViewSession.session_id == session_id,
            )
        )
        return result.scalar_one_or_none()

    async def generate_video_thumbnail(self, video: Video) -> str:
        """Generate thumbnail for video"""
        try:
            # Download video file temporarily
            temp_video_path = f"/tmp/{video.id}.{video.file_extension[1:]}"
            video_content = await self.minio_service.get_file_content(video.file_path)

            with open(temp_video_path, "wb") as f:
                f.write(video_content)

            # Generate thumbnail using OpenCV
            cap = cv2.VideoCapture(temp_video_path)

            # Seek to middle of video
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            middle_frame = frame_count // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)

            ret, frame = cap.read()
            if ret:
                # Save thumbnail
                thumbnail_filename = f"thumbnail_{video.id}.jpg"
                thumbnail_path = f"thumbnails/{video.id}/{thumbnail_filename}"
                temp_thumbnail_path = f"/tmp/{thumbnail_filename}"

                cv2.imwrite(temp_thumbnail_path, frame)

                # Upload thumbnail to storage
                with open(temp_thumbnail_path, "rb") as f:
                    thumbnail_content = f.read()

                await self.minio_service.upload_file(
                    thumbnail_path, thumbnail_content, content_type="image/jpeg"
                )

                # Update video record
                video.thumbnail_path = thumbnail_path
                video.thumbnail_generated = True
                await self.db.commit()

                # Cleanup
                os.remove(temp_video_path)
                os.remove(temp_thumbnail_path)

                return thumbnail_path

            cap.release()
            os.remove(temp_video_path)

        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None

    async def get_video_statistics(self, video_id: str) -> Dict[str, Any]:
        """Get video statistics"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        # Get view sessions count
        view_sessions_result = await self.db.execute(
            select(VideoViewSession).where(VideoViewSession.video_id == video_id)
        )
        view_sessions = view_sessions_result.scalars().all()

        # Calculate statistics
        total_views = len(view_sessions)
        unique_viewers = len(
            set(session.user_id for session in view_sessions if session.user_id)
        )
        total_watch_time = sum(session.watch_duration for session in view_sessions)
        completed_views = len([s for s in view_sessions if s.is_completed])
        completion_rate = (
            (completed_views / total_views * 100) if total_views > 0 else 0
        )

        return {
            "video_id": video_id,
            "total_views": total_views,
            "unique_viewers": unique_viewers,
            "total_watch_time": total_watch_time,
            "average_watch_time": (
                total_watch_time / total_views if total_views > 0 else 0
            ),
            "completion_rate": completion_rate,
            "file_size_mb": video.file_size_mb,
            "duration": video.duration,
            "resolution": video.resolution,
            "created_at": video.created_at,
            "updated_at": video.updated_at,
        }

    async def _validate_video_file(self, file: UploadFile):
        """Validate uploaded video file"""
        # Check file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB",
            )

        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {file_ext} not supported. Allowed types: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}",
            )

        # Check MIME type
        expected_mime_types = [
            "video/mp4",
            "video/quicktime",
            "video/x-msvideo",
            "video/x-matroska",
            "video/webm",
        ]
        if file.content_type not in expected_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid MIME type: {file.content_type}",
            )

    async def _process_video_metadata(self, video: Video):
        """Process video metadata (runs in background)"""
        try:
            # Download video file temporarily for processing
            temp_video_path = f"/tmp/{video.id}.{video.file_extension[1:]}"
            video_content = await self.minio_service.get_file_content(video.file_path)

            with open(temp_video_path, "wb") as f:
                f.write(video_content)

            # Extract video metadata using OpenCV
            cap = cv2.VideoCapture(temp_video_path)

            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            # Update video with metadata
            video.duration = duration
            video.width = width
            video.height = height
            video.fps = fps
            video.metadata = {
                "frame_count": frame_count,
                "codec": "unknown",  # Would need ffmpeg for detailed codec info
                "container": video.file_extension[1:].upper(),
            }

            cap.release()
            os.remove(temp_video_path)

            # Generate thumbnail
            if settings.ENABLE_VIDEO_THUMBNAILS:
                await self.generate_video_thumbnail(video)

            # Mark processing as completed
            video.status = VideoStatus.COMPLETED
            video.processed_at = datetime.utcnow()
            video.processing_progress = 100

            await self.db.commit()

        except Exception as e:
            # Mark processing as failed
            video.status = VideoStatus.FAILED
            video.error_message = f"Processing failed: {str(e)}"
            await self.db.commit()
            print(f"Video processing failed for {video.id}: {e}")


class VideoAnalyticsService:
    """Service for video analytics and reporting"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def record_video_view(
        self,
        video_id: str,
        session_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VideoViewSession:
        """Record a video view"""

        # Check if view session already exists
        result = await self.db.execute(
            select(VideoViewSession).where(
                VideoViewSession.video_id == video_id,
                VideoViewSession.session_id == session_id,
            )
        )
        view_session = result.scalar_one_or_none()

        if not view_session:
            view_session = VideoViewSession(
                id=str(uuid.uuid4()),
                video_id=video_id,
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.add(view_session)

            # Increment video view count
            video = await self.db.get(Video, video_id)
            if video:
                video.view_count += 1

            await self.db.commit()

        return view_session

    async def get_video_analytics(
        self,
        video_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get comprehensive video analytics"""

        # Base query for view sessions
        query = select(VideoViewSession).where(VideoViewSession.video_id == video_id)

        # Apply date filters
        if start_date:
            query = query.where(VideoViewSession.created_at >= start_date)
        if end_date:
            query = query.where(VideoViewSession.created_at <= end_date)

        result = await self.db.execute(query)
        view_sessions = result.scalars().all()

        # Calculate metrics
        total_views = len(view_sessions)
        unique_viewers = len(set(s.user_id for s in view_sessions if s.user_id))
        total_watch_time = sum(s.watch_duration for s in view_sessions)
        completed_views = len([s for s in view_sessions if s.is_completed])

        # Calculate averages
        avg_watch_time = total_watch_time / total_views if total_views > 0 else 0
        completion_rate = (
            (completed_views / total_views * 100) if total_views > 0 else 0
        )

        # Calculate engagement metrics
        engaged_views = len([s for s in view_sessions if s.completion_percentage >= 25])
        engagement_rate = (engaged_views / total_views * 100) if total_views > 0 else 0

        # Get video info
        video = await self.db.get(Video, video_id)

        return {
            "video_id": video_id,
            "video_title": video.title if video else "Unknown",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "metrics": {
                "total_views": total_views,
                "unique_viewers": unique_viewers,
                "total_watch_time_hours": round(total_watch_time / 3600, 2),
                "average_watch_time_minutes": round(avg_watch_time / 60, 2),
                "completion_rate": round(completion_rate, 2),
                "engagement_rate": round(engagement_rate, 2),
            },
            "video_info": {
                "duration_minutes": (
                    round(video.duration / 60, 2) if video and video.duration else 0
                ),
                "file_size_mb": video.file_size_mb if video else 0,
                "created_at": video.created_at.isoformat() if video else None,
            },
        }

    async def get_top_videos(
        self, limit: int = 10, metric: str = "views", days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get top performing videos"""

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get videos with view counts
        query = """
        SELECT 
            v.id,
            v.title,
            v.duration,
            v.created_at,
            COUNT(vs.id) as view_count,
            COUNT(DISTINCT vs.user_id) as unique_viewers,
            SUM(vs.watch_duration) as total_watch_time,
            AVG(vs.completion_percentage) as avg_completion
        FROM videos v
        LEFT JOIN video_view_sessions vs ON v.id = vs.video_id
        WHERE v.status = 'completed'
        AND (vs.created_at >= :start_date OR vs.created_at IS NULL)
        GROUP BY v.id, v.title, v.duration, v.created_at
        ORDER BY view_count DESC
        LIMIT :limit
        """

        result = await self.db.execute(
            query, {"start_date": start_date, "limit": limit}
        )

        return [
            {
                "video_id": row.id,
                "title": row.title,
                "view_count": row.view_count,
                "unique_viewers": row.unique_viewers,
                "total_watch_time_hours": round((row.total_watch_time or 0) / 3600, 2),
                "avg_completion_rate": round(row.avg_completion or 0, 2),
                "duration_minutes": round((row.duration or 0) / 60, 2),
                "created_at": row.created_at.isoformat(),
            }
            for row in result.fetchall()
        ]


class VideoSearchService:
    """Service for video search and discovery"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def search_videos(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Video]:
        """Search videos by title, description, and tags"""

        # Base query
        search_query = select(Video).where(Video.status == VideoStatus.COMPLETED)

        # Text search
        if query:
            search_condition = Video.title.ilike(
                f"%{query}%"
            ) | Video.description.ilike(f"%{query}%")
            search_query = search_query.where(search_condition)

        # Apply filters
        if filters:
            if filters.get("duration_min"):
                search_query = search_query.where(
                    Video.duration >= filters["duration_min"]
                )
            if filters.get("duration_max"):
                search_query = search_query.where(
                    Video.duration <= filters["duration_max"]
                )
            if filters.get("created_after"):
                search_query = search_query.where(
                    Video.created_at >= filters["created_after"]
                )
            if filters.get("created_before"):
                search_query = search_query.where(
                    Video.created_at <= filters["created_before"]
                )

        # Order by relevance (view count for now)
        search_query = search_query.order_by(
            Video.view_count.desc(), Video.created_at.desc()
        )

        # Apply pagination
        search_query = search_query.offset(offset).limit(limit)

        result = await self.db.execute(search_query)
        return result.scalars().all()

    async def get_recommended_videos(
        self, video_id: str, limit: int = 5
    ) -> List[Video]:
        """Get recommended videos based on current video"""

        # Simple recommendation: videos with similar duration and high view count
        current_video = await self.db.get(Video, video_id)
        if not current_video:
            return []

        # Find videos with similar duration (±20%)
        duration_range = current_video.duration * 0.2 if current_video.duration else 0
        min_duration = (current_video.duration or 0) - duration_range
        max_duration = (current_video.duration or 0) + duration_range

        query = (
            select(Video)
            .where(
                Video.status == VideoStatus.COMPLETED,
                Video.id != video_id,
                Video.duration.between(min_duration, max_duration),
            )
            .order_by(Video.view_count.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        recommended = result.scalars().all()

        # If not enough similar videos, fill with popular videos
        if len(recommended) < limit:
            remaining = limit - len(recommended)
            popular_query = (
                select(Video)
                .where(
                    Video.status == VideoStatus.COMPLETED,
                    Video.id != video_id,
                    Video.id.notin_([v.id for v in recommended]),
                )
                .order_by(Video.view_count.desc())
                .limit(remaining)
            )

            result = await self.db.execute(popular_query)
            recommended.extend(result.scalars().all())

        return recommended
