"""
🔄 Celery Background Tasks
Handles asynchronous video processing and upload tasks
"""

import asyncio
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, Optional

import cv2
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.video import Video, VideoStatus
from app.services.minio_service import MinIOService

# Create Celery app
celery_app = Celery(
    "video_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["celery_worker.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    task_routes={
        "celery_worker.tasks.process_video_upload": {"queue": "video_processing"},
        "celery_worker.tasks.generate_video_thumbnail": {"queue": "thumbnails"},
        "celery_worker.tasks.cleanup_temp_files": {"queue": "cleanup"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
)

# Database setup for tasks
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session for tasks"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@celery_app.task(bind=True, name="process_video_upload")
def process_video_upload(self, video_id: str, file_path: str) -> Dict[str, Any]:
    """
    Process uploaded video file
    - Extract metadata
    - Generate thumbnail
    - Update video status
    """
    db = SessionLocal()
    minio_service = MinIOService()

    try:
        # Get video record
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise Exception(f"Video {video_id} not found")

        # Update status to processing
        video.status = VideoStatus.PROCESSING
        video.processing_progress = 10
        db.commit()

        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Starting video processing"},
        )

        # Download video file for processing
        video_content = asyncio.run(minio_service.get_file_content(file_path))

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=video.file_extension, delete=False
        ) as temp_file:
            temp_file.write(video_content)
            temp_video_path = temp_file.name

        try:
            # Extract video metadata
            metadata = extract_video_metadata(temp_video_path)

            # Update video with metadata
            video.duration = metadata.get("duration", 0)
            video.width = metadata.get("width", 0)
            video.height = metadata.get("height", 0)
            video.fps = metadata.get("fps", 0)
            video.bitrate = metadata.get("bitrate", 0)
            video.codec = metadata.get("codec", "unknown")
            video.metadata = metadata
            video.processing_progress = 50
            db.commit()

            self.update_state(
                state="PROGRESS",
                meta={"current": 50, "total": 100, "status": "Metadata extracted"},
            )

            # Generate thumbnail if enabled
            if settings.ENABLE_VIDEO_THUMBNAILS:
                thumbnail_path = generate_video_thumbnail_sync(
                    temp_video_path, video_id, minio_service
                )
                if thumbnail_path:
                    video.thumbnail_path = thumbnail_path
                    video.thumbnail_generated = True

                video.processing_progress = 80
                db.commit()

                self.update_state(
                    state="PROGRESS",
                    meta={"current": 80, "total": 100, "status": "Thumbnail generated"},
                )

            # Mark as completed
            video.status = VideoStatus.COMPLETED
            video.processed_at = datetime.utcnow()
            video.processing_progress = 100
            db.commit()

            return {
                "status": "completed",
                "video_id": video_id,
                "duration": video.duration,
                "resolution": (
                    f"{video.width}x{video.height}"
                    if video.width and video.height
                    else None
                ),
                "thumbnail_generated": video.thumbnail_generated,
                "processed_at": video.processed_at.isoformat(),
            }

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

    except Exception as e:
        # Mark as failed
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            db.commit()

        # Update task state
        self.update_state(state="FAILURE", meta={"error": str(e), "video_id": video_id})

        raise Exception(f"Video processing failed: {str(e)}")

    finally:
        db.close()


@celery_app.task(bind=True, name="generate_video_thumbnail")
def generate_video_thumbnail_task(self, video_id: str) -> Dict[str, Any]:
    """Generate thumbnail for video (can be called separately)"""
    db = SessionLocal()
    minio_service = MinIOService()

    try:
        # Get video record
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise Exception(f"Video {video_id} not found")

        if not video.file_path:
            raise Exception("Video file path not found")

        # Download video file
        video_content = asyncio.run(minio_service.get_file_content(video.file_path))

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=video.file_extension, delete=False
        ) as temp_file:
            temp_file.write(video_content)
            temp_video_path = temp_file.name

        try:
            # Generate thumbnail
            thumbnail_path = generate_video_thumbnail_sync(
                temp_video_path, video_id, minio_service
            )

            if thumbnail_path:
                video.thumbnail_path = thumbnail_path
                video.thumbnail_generated = True
                db.commit()

                return {
                    "status": "completed",
                    "video_id": video_id,
                    "thumbnail_path": thumbnail_path,
                }
            else:
                raise Exception("Failed to generate thumbnail")

        finally:
            # Cleanup
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e), "video_id": video_id})
        raise

    finally:
        db.close()


@celery_app.task(name="cleanup_temp_files")
def cleanup_temp_files(file_paths: list) -> Dict[str, Any]:
    """Clean up temporary files"""
    cleaned = 0
    errors = []

    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                cleaned += 1
        except Exception as e:
            errors.append(f"Failed to delete {file_path}: {str(e)}")

    return {"status": "completed", "cleaned_files": cleaned, "errors": errors}


@celery_app.task(name="process_video_analytics")
def process_video_analytics(
    video_id: str, analytics_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Process video analytics data"""
    db = SessionLocal()

    try:
        # Get video
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise Exception(f"Video {video_id} not found")

        # Update view count
        video.view_count += analytics_data.get("views", 0)

        # You could add more analytics processing here
        # - Update hourly/daily analytics tables
        # - Calculate trending scores
        # - Generate reports

        db.commit()

        return {
            "status": "completed",
            "video_id": video_id,
            "updated_view_count": video.view_count,
        }

    except Exception as e:
        raise Exception(f"Analytics processing failed: {str(e)}")

    finally:
        db.close()


@celery_app.task(name="health_check_videos")
def health_check_videos() -> Dict[str, Any]:
    """Health check for video files"""
    db = SessionLocal()
    minio_service = MinIOService()

    try:
        # Get all completed videos
        videos = db.query(Video).filter(Video.status == VideoStatus.COMPLETED).all()

        healthy_count = 0
        unhealthy_count = 0
        missing_files = []

        for video in videos:
            if video.file_path:
                # Check if file exists in storage
                file_exists = asyncio.run(minio_service.file_exists(video.file_path))
                if file_exists:
                    healthy_count += 1
                else:
                    unhealthy_count += 1
                    missing_files.append(
                        {
                            "video_id": video.id,
                            "title": video.title,
                            "file_path": video.file_path,
                        }
                    )

        return {
            "status": "completed",
            "total_videos": len(videos),
            "healthy_videos": healthy_count,
            "unhealthy_videos": unhealthy_count,
            "missing_files": missing_files,
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()


# Utility functions
def extract_video_metadata(video_path: str) -> Dict[str, Any]:
    """Extract video metadata using OpenCV"""
    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("Could not open video file")

        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0

        # Get first frame for additional analysis
        ret, frame = cap.read()

        cap.release()

        metadata = {
            "frame_count": frame_count,
            "fps": fps,
            "width": width,
            "height": height,
            "duration": duration,
            "codec": "unknown",  # Would need ffmpeg for detailed codec info
            "has_audio": True,  # Assume true, would need ffmpeg to detect
            "bitrate": None,  # Would need ffmpeg
            "file_format": os.path.splitext(video_path)[1][1:].upper(),
            "analysis_date": datetime.utcnow().isoformat(),
        }

        return metadata

    except Exception as e:
        raise Exception(f"Failed to extract metadata: {str(e)}")


def generate_video_thumbnail_sync(
    video_path: str, video_id: str, minio_service: MinIOService
) -> Optional[str]:
    """Generate thumbnail synchronously"""
    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return None

        # Seek to middle of video
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame = frame_count // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)

        ret, frame = cap.read()
        if ret:
            # Create thumbnail
            thumbnail_filename = f"thumbnail_{video_id}.jpg"
            temp_thumbnail_path = f"/tmp/{thumbnail_filename}"

            # Resize frame for thumbnail (max 320x240)
            height, width = frame.shape[:2]
            if width > 320:
                ratio = 320 / width
                new_width = 320
                new_height = int(height * ratio)
                frame = cv2.resize(frame, (new_width, new_height))

            # Save thumbnail
            cv2.imwrite(
                temp_thumbnail_path,
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, settings.THUMBNAIL_QUALITY],
            )

            # Upload to storage
            thumbnail_path = f"thumbnails/{video_id}/{thumbnail_filename}"

            with open(temp_thumbnail_path, "rb") as f:
                thumbnail_content = f.read()

            asyncio.run(
                minio_service.upload_file(
                    thumbnail_path, thumbnail_content, content_type="image/jpeg"
                )
            )

            # Cleanup temp file
            os.remove(temp_thumbnail_path)

            cap.release()
            return thumbnail_path

        cap.release()
        return None

    except Exception as e:
        print(f"Thumbnail generation failed: {e}")
        return None


# Periodic tasks
@celery_app.task(name="periodic_cleanup")
def periodic_cleanup() -> Dict[str, Any]:
    """Periodic cleanup of old temporary files and failed uploads"""
    db = SessionLocal()

    try:
        # Clean up failed uploads older than 24 hours
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        failed_videos = (
            db.query(Video)
            .filter(Video.status == VideoStatus.FAILED, Video.created_at < cutoff_time)
            .all()
        )

        cleaned_count = 0
        for video in failed_videos:
            # Delete from database
            db.delete(video)
            cleaned_count += 1

        db.commit()

        return {
            "status": "completed",
            "cleaned_failed_uploads": cleaned_count,
            "cleanup_time": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()


# Setup periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "periodic-cleanup": {
        "task": "periodic_cleanup",
        "schedule": crontab(minute=0, hour=2),  # Run daily at 2 AM
    },
    "health-check": {
        "task": "health_check_videos",
        "schedule": crontab(minute=0, hour="*/6"),  # Run every 6 hours
    },
}
