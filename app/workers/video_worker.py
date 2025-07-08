"""
🎬 Video Processing Worker
Dedicated worker for video-specific operations
"""

import asyncio
import os
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.video import Video, VideoStatus
from app.services.minio_service import MinIOService

# Conditional import of cv2 to handle Docker issues
try:
    import cv2

    CV2_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenCV not available in video worker: {e}")
    CV2_AVAILABLE = False


class VideoProcessingWorker:
    """Worker class for video processing operations"""

    def __init__(self):
        self.minio_service = MinIOService()

    async def process_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Process video metadata extraction"""
        if not CV2_AVAILABLE:
            return {
                "status": "failed",
                "error": "OpenCV not available",
                "video_id": video_id,
            }

        async with AsyncSessionLocal() as db:
            try:
                # Get video record
                result = await db.execute(select(Video).where(Video.id == video_id))
                video = result.scalar_one_or_none()

                if not video:
                    raise Exception(f"Video {video_id} not found")

                # Update status
                video.status = VideoStatus.PROCESSING
                video.processing_progress = 20
                await db.commit()

                # Download video file temporarily
                temp_video_path = f"/tmp/{video_id}_metadata.{video.file_extension[1:]}"
                video_content = await self.minio_service.get_file_content(
                    video.file_path
                )

                with open(temp_video_path, "wb") as f:
                    f.write(video_content)

                try:
                    # Extract metadata using OpenCV
                    metadata = await self._extract_video_metadata(temp_video_path)

                    # Update video with metadata
                    video.duration = metadata.get("duration", 0)
                    video.width = metadata.get("width", 0)
                    video.height = metadata.get("height", 0)
                    video.fps = metadata.get("fps", 0)
                    video.bitrate = metadata.get("bitrate", 0)
                    video.codec = metadata.get("codec", "unknown")
                    video.metadata = metadata
                    video.processing_progress = 60

                    await db.commit()

                    return {
                        "status": "completed",
                        "video_id": video_id,
                        "metadata": metadata,
                        "duration": video.duration,
                        "resolution": (
                            f"{video.width}x{video.height}"
                            if video.width and video.height
                            else None
                        ),
                    }

                finally:
                    # Cleanup temporary file
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)

            except Exception as e:
                # Update video status on failure
                if video:
                    video.status = VideoStatus.FAILED
                    video.error_message = str(e)
                    await db.commit()

                return {"status": "failed", "error": str(e), "video_id": video_id}

    async def generate_video_thumbnail(self, video_id: str) -> Dict[str, Any]:
        """Generate thumbnail for video"""
        if not CV2_AVAILABLE:
            return {
                "status": "failed",
                "error": "OpenCV not available",
                "video_id": video_id,
            }

        async with AsyncSessionLocal() as db:
            try:
                # Get video record
                result = await db.execute(select(Video).where(Video.id == video_id))
                video = result.scalar_one_or_none()

                if not video:
                    raise Exception(f"Video {video_id} not found")

                if not video.file_path:
                    raise Exception("Video file path not found")

                # Download video file temporarily
                temp_video_path = f"/tmp/{video_id}_thumb.{video.file_extension[1:]}"
                video_content = await self.minio_service.get_file_content(
                    video.file_path
                )

                with open(temp_video_path, "wb") as f:
                    f.write(video_content)

                try:
                    # Generate thumbnail
                    thumbnail_path = await self._generate_thumbnail(
                        temp_video_path, video_id
                    )

                    if thumbnail_path:
                        video.thumbnail_path = thumbnail_path
                        video.thumbnail_generated = True
                        await db.commit()

                        return {
                            "status": "completed",
                            "video_id": video_id,
                            "thumbnail_path": thumbnail_path,
                        }
                    else:
                        raise Exception("Failed to generate thumbnail")

                finally:
                    # Cleanup temporary file
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)

            except Exception as e:
                return {"status": "failed", "error": str(e), "video_id": video_id}

    async def validate_video_file(self, video_id: str) -> Dict[str, Any]:
        """Validate video file integrity"""
        if not CV2_AVAILABLE:
            return {
                "status": "failed",
                "error": "OpenCV not available",
                "video_id": video_id,
            }

        async with AsyncSessionLocal() as db:
            try:
                # Get video record
                result = await db.execute(select(Video).where(Video.id == video_id))
                video = result.scalar_one_or_none()

                if not video:
                    raise Exception(f"Video {video_id} not found")

                # Download and validate
                temp_video_path = f"/tmp/{video_id}_validate.{video.file_extension[1:]}"
                video_content = await self.minio_service.get_file_content(
                    video.file_path
                )

                with open(temp_video_path, "wb") as f:
                    f.write(video_content)

                try:
                    # Validate using OpenCV
                    validation_result = await self._validate_video_integrity(
                        temp_video_path
                    )

                    return {
                        "status": "completed",
                        "video_id": video_id,
                        "validation": validation_result,
                    }

                finally:
                    # Cleanup
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)

            except Exception as e:
                return {"status": "failed", "error": str(e), "video_id": video_id}

    async def transcode_video(
        self, video_id: str, target_quality: str
    ) -> Dict[str, Any]:
        """Transcode video to different quality (placeholder for future implementation)"""
        # This would use FFmpeg for actual transcoding
        # For now, just return a placeholder response

        return {
            "status": "not_implemented",
            "message": "Video transcoding not yet implemented",
            "video_id": video_id,
            "target_quality": target_quality,
        }

    async def _extract_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using OpenCV"""

        def _extract_sync():
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
            has_video = ret and frame is not None

            cap.release()

            return {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration": duration,
                "codec": "unknown",  # Would need FFmpeg for detailed codec info
                "has_video": has_video,
                "bitrate": None,  # Would need FFmpeg
                "file_format": os.path.splitext(video_path)[1][1:].upper(),
                "analysis_date": datetime.utcnow().isoformat(),
            }

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract_sync)

    async def _generate_thumbnail(
        self, video_path: str, video_id: str
    ) -> Optional[str]:
        """Generate thumbnail using OpenCV"""

        def _generate_sync():
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

                cap.release()
                return temp_thumbnail_path

            cap.release()
            return None

        # Run in thread pool
        loop = asyncio.get_event_loop()
        temp_path = await loop.run_in_executor(None, _generate_sync)

        if temp_path and os.path.exists(temp_path):
            try:
                # Upload to storage
                thumbnail_path = f"thumbnails/{video_id}/thumbnail_{video_id}.jpg"

                with open(temp_path, "rb") as f:
                    thumbnail_content = f.read()

                await self.minio_service.upload_file(
                    thumbnail_path, thumbnail_content, content_type="image/jpeg"
                )

                # Cleanup temp file
                os.remove(temp_path)

                return thumbnail_path

            except Exception as e:
                # Cleanup on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e

        return None

    async def _validate_video_integrity(self, video_path: str) -> Dict[str, Any]:
        """Validate video file integrity"""

        def _validate_sync():
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                return {
                    "is_valid": False,
                    "error": "Cannot open video file",
                    "readable": False,
                }

            # Try to read some frames
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            readable_frames = 0
            sample_frames = min(10, total_frames)  # Sample up to 10 frames

            for i in range(sample_frames):
                frame_pos = int((i / sample_frames) * total_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                if ret and frame is not None:
                    readable_frames += 1

            cap.release()

            # Calculate integrity score
            integrity_score = (
                (readable_frames / sample_frames) * 100 if sample_frames > 0 else 0
            )

            return {
                "is_valid": integrity_score >= 80,  # 80% threshold
                "integrity_score": integrity_score,
                "readable_frames": readable_frames,
                "sampled_frames": sample_frames,
                "total_frames": total_frames,
                "readable": True,
            }

        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _validate_sync)


# Worker operations functions that can be called from Celery tasks
async def process_video_metadata_task(video_id: str) -> Dict[str, Any]:
    """Async wrapper for video metadata processing"""
    worker = VideoProcessingWorker()
    return await worker.process_video_metadata(video_id)


async def generate_video_thumbnail_task(video_id: str) -> Dict[str, Any]:
    """Async wrapper for video thumbnail generation"""
    worker = VideoProcessingWorker()
    return await worker.generate_video_thumbnail(video_id)


async def validate_video_file_task(video_id: str) -> Dict[str, Any]:
    """Async wrapper for video file validation"""
    worker = VideoProcessingWorker()
    return await worker.validate_video_file(video_id)
