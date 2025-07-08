"""
🎬 Video API Endpoints
RESTful API for video management, upload, and streaming
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.dependencys.videos import (
    get_analytics_service,
    get_current_admin,
    get_search_service,
    get_video_service,
)
from app.models.video import VideoStatus
from app.schemas.videos import (
    BatchDeleteRequest,
    BatchDeleteResponse,
    DashboardOverviewResponse,
    VideoListResponse,
    VideoProgressRequest,
    VideoProgressResponse,
    VideoResponse,
    VideoStatsResponse,
    VideoUploadResponse,
)
from app.services.minio_service import MinIOService
from app.services.video_service import (
    VideoAnalyticsService,
    VideoSearchService,
    VideoService,
)
from celery_worker.tasks import generate_video_thumbnail_task, process_video_upload

# Initialize router
router = APIRouter()


# Video Management Endpoints
@router.get("/", response_model=VideoListResponse)
async def list_videos(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """List all videos with filtering and pagination"""

    # Convert status string to enum if provided
    video_status = None
    if status:
        try:
            video_status = VideoStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}",
            )

    # Get videos
    videos = await video_service.get_videos(
        skip=skip, limit=limit, status=video_status, search=search
    )

    # Get total count (simplified - in production you'd want a separate count query)
    total = len(videos) + skip

    return VideoListResponse(
        videos=[VideoResponse.from_orm(video) for video in videos],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str, video_service: VideoService = Depends(get_video_service)
):
    """Get video by ID"""
    video = await video_service.get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    return VideoResponse.from_orm(video)


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """Upload a new video file"""

    # Create video record
    video = await video_service.create_video(
        title=title, description=description, file=file
    )

    try:
        # Start upload process
        upload_session = await video_service.upload_video_file(video, file)

        # Trigger background processing
        task = process_video_upload.delay(video.id, video.file_path)

        return VideoUploadResponse(
            video_id=video.id,
            upload_session_id=upload_session.id,
            status="uploading",
            message=f"Video upload started. Task ID: {task.id}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """Delete a video"""
    success = await video_service.delete_video(video_id)
    if success:
        return {"message": "Video deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video",
        )


# Video Streaming Endpoints
@router.get("/{video_id}/stream")
async def stream_video(
    video_id: str,
    request: Request,
    video_service: VideoService = Depends(get_video_service),
    analytics_service: VideoAnalyticsService = Depends(get_analytics_service),
):
    """Stream video content as blob"""

    # Get video
    video = await video_service.get_video_by_id(video_id)
    if not video or video.status != VideoStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found or not ready"
        )

    # Record view (simplified - you might want more sophisticated tracking)
    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))
    user_ip = request.client.host
    user_agent = request.headers.get("User-Agent")

    await analytics_service.record_video_view(
        video_id=video_id,
        session_id=session_id,
        ip_address=user_ip,
        user_agent=user_agent,
    )

    try:
        # Get video content
        content = await video_service.stream_video_content(video_id)

        # Create streaming response
        def generate():
            chunk_size = settings.STREAMING_CHUNK_SIZE
            for i in range(0, len(content), chunk_size):
                yield content[i : i + chunk_size]

        # Prepare headers
        headers = {
            "Content-Type": video.file_type,
            "Content-Length": str(len(content)),
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }

        # Handle range requests for video seeking
        range_header = request.headers.get("Range")
        if range_header:
            # Parse range header
            range_match = range_header.replace("bytes=", "").split("-")
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else len(content) - 1

            # Return partial content
            partial_content = content[start : end + 1]

            headers.update(
                {
                    "Content-Range": f"bytes {start}-{end}/{len(content)}",
                    "Content-Length": str(len(partial_content)),
                }
            )

            return Response(
                content=partial_content,
                status_code=206,
                headers=headers,
                media_type=video.file_type,
            )

        return StreamingResponse(
            generate(), media_type=video.file_type, headers=headers
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming failed: {str(e)}",
        )


@router.get("/{video_id}/thumbnail")
async def get_video_thumbnail(
    video_id: str, video_service: VideoService = Depends(get_video_service)
):
    """Get video thumbnail"""
    video = await video_service.get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    if not video.thumbnail_path:
        # Generate thumbnail if it doesn't exist
        task = generate_video_thumbnail_task.delay(video_id)
        return {"message": "Thumbnail generation started", "task_id": task.id}

    try:
        # Get thumbnail from storage
        minio_service = MinIOService()
        thumbnail_content = await minio_service.get_file_content(video.thumbnail_path)

        return Response(
            content=thumbnail_content,
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=3600"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get thumbnail: {str(e)}",
        )


@router.get("/{video_id}/url")
async def get_video_url(
    video_id: str,
    expires_in: int = 3600,
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """Get presigned URL for video access"""
    try:
        url = await video_service.get_video_stream_url(
            video_id=video_id, expires_in=expires_in
        )
        return {"video_url": url, "expires_in": expires_in}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Video Progress Tracking
@router.post("/{video_id}/progress", response_model=VideoProgressResponse)
async def update_video_progress(
    video_id: str,
    progress_data: VideoProgressRequest,
    video_service: VideoService = Depends(get_video_service),
):
    """Update video viewing progress"""
    view_session = await video_service.update_video_progress(
        video_id=video_id,
        session_id=progress_data.session_id,
        current_time=progress_data.current_time,
    )

    return VideoProgressResponse(
        video_id=video_id,
        current_time=view_session.current_time,
        completion_percentage=view_session.completion_percentage,
        resume_position=view_session.resume_position,
    )


@router.get("/{video_id}/progress")
async def get_video_progress(
    video_id: str,
    session_id: str,
    video_service: VideoService = Depends(get_video_service),
):
    """Get video viewing progress"""
    view_session = await video_service.get_video_progress(
        video_id=video_id, session_id=session_id
    )

    if not view_session:
        return {"video_id": video_id, "current_time": 0, "completion_percentage": 0}

    return {
        "video_id": video_id,
        "current_time": view_session.current_time,
        "completion_percentage": view_session.completion_percentage,
        "resume_position": view_session.resume_position,
        "last_accessed": view_session.last_accessed.isoformat(),
    }


# Video Analytics
@router.get("/{video_id}/stats", response_model=VideoStatsResponse)
async def get_video_statistics(
    video_id: str,
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """Get video statistics"""
    stats = await video_service.get_video_statistics(video_id)
    return VideoStatsResponse(**stats)


@router.get("/{video_id}/analytics")
async def get_video_analytics(
    video_id: str,
    days: int = 30,
    analytics_service: VideoAnalyticsService = Depends(get_analytics_service),
    current_user=Depends(get_current_admin),
):
    """Get detailed video analytics"""
    from datetime import datetime, timedelta

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    analytics = await analytics_service.get_video_analytics(
        video_id=video_id, start_date=start_date, end_date=end_date
    )

    return analytics


# Video Search
@router.get("/search/query")
async def search_videos(
    q: str,
    limit: int = 20,
    offset: int = 0,
    search_service: VideoSearchService = Depends(get_search_service),
):
    """Search videos by title and description"""
    videos = await search_service.search_videos(query=q, limit=limit, offset=offset)

    return {
        "query": q,
        "results": [VideoResponse.from_orm(video) for video in videos],
        "total": len(videos),
        "offset": offset,
        "limit": limit,
    }


@router.get("/{video_id}/recommendations")
async def get_video_recommendations(
    video_id: str,
    limit: int = 5,
    search_service: VideoSearchService = Depends(get_search_service),
):
    """Get recommended videos based on current video"""
    recommendations = await search_service.get_recommended_videos(
        video_id=video_id, limit=limit
    )

    return {
        "video_id": video_id,
        "recommendations": [VideoResponse.from_orm(video) for video in recommendations],
    }


# Upload Status
@router.get("/{video_id}/status")
async def get_upload_status(
    video_id: str, video_service: VideoService = Depends(get_video_service)
):
    """Get video upload/processing status"""
    video = await video_service.get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    return {
        "video_id": video_id,
        "status": video.status,
        "processing_progress": video.processing_progress,
        "error_message": video.error_message,
        "created_at": video.created_at.isoformat(),
        "updated_at": video.updated_at.isoformat(),
        "uploaded_at": video.uploaded_at.isoformat() if video.uploaded_at else None,
        "processed_at": video.processed_at.isoformat() if video.processed_at else None,
    }


# Batch Operations
@router.post("/batch/delete", response_model=BatchDeleteResponse)
async def batch_delete_videos(
    request: BatchDeleteRequest,
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """Delete multiple videos"""
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required for batch delete operation",
        )

    results = []
    successful = 0
    failed = 0
    errors = []

    for video_id in request.video_ids:
        try:
            success = await video_service.delete_video(video_id)
            if success:
                successful += 1
                results.append({"video_id": video_id, "success": True})
            else:
                failed += 1
                error_msg = f"Failed to delete video {video_id}"
                errors.append(error_msg)
                results.append(
                    {"video_id": video_id, "success": False, "error": error_msg}
                )
        except Exception as e:
            failed += 1
            error_msg = str(e)
            errors.append(f"Video {video_id}: {error_msg}")
            results.append({"video_id": video_id, "success": False, "error": error_msg})

    return BatchDeleteResponse(
        results=results,
        total_requested=len(request.video_ids),
        successful=successful,
        failed=failed,
        errors=errors,
    )


# Dashboard Data
@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    analytics_service: VideoAnalyticsService = Depends(get_analytics_service),
    video_service: VideoService = Depends(get_video_service),
    current_user=Depends(get_current_admin),
):
    """Get dashboard overview data"""
    try:
        # Get top videos
        top_videos = await analytics_service.get_top_videos(limit=10, days=30)

        # Get recent uploads
        recent_videos = await video_service.get_videos(skip=0, limit=5)

        # Calculate summary stats
        all_videos = await video_service.get_videos(
            skip=0, limit=1000
        )  # Get more for stats

        summary = {
            "total_videos": len(all_videos),
            "completed_videos": len(
                [v for v in all_videos if v.status == VideoStatus.COMPLETED]
            ),
            "processing_videos": len(
                [
                    v
                    for v in all_videos
                    if v.status
                    in [
                        VideoStatus.PENDING,
                        VideoStatus.UPLOADING,
                        VideoStatus.PROCESSING,
                    ]
                ]
            ),
            "failed_videos": len(
                [v for v in all_videos if v.status == VideoStatus.FAILED]
            ),
            "total_views": sum(v.view_count for v in all_videos),
            "total_storage_mb": sum(v.file_size for v in all_videos) / (1024 * 1024),
        }

        analytics = {
            "upload_trend": "increasing",  # Would calculate from real data
            "popular_formats": {"mp4": 75, "webm": 20, "mov": 5},
            "avg_duration_minutes": (
                sum(v.duration or 0 for v in all_videos) / len(all_videos) / 60
                if all_videos
                else 0
            ),
        }

        return DashboardOverviewResponse(
            summary=summary,
            # top_videos=top_videos,
            recent_uploads=[VideoResponse.from_orm(v) for v in recent_videos],
            analytics=analytics,
            period="last_30_days",
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard overview: {str(e)}",
        )
