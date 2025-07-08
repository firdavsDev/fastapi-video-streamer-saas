"""
🗄️ MinIO Storage Service
Handles file storage operations with MinIO object storage
"""

import asyncio
import io
from datetime import timedelta
from typing import BinaryIO, Optional, Union

from fastapi import HTTPException, status
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinIOService:
    """MinIO storage service for video file management"""

    def __init__(self):
        """Initialize MinIO client"""
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._bucket_checked = False

    async def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        if self._bucket_checked:
            return

        try:
            # Run sync operation in thread pool
            loop = asyncio.get_event_loop()

            # Check if bucket exists
            bucket_exists = await loop.run_in_executor(
                None, self.client.bucket_exists, self.bucket_name
            )

            if not bucket_exists:
                # Create bucket
                await loop.run_in_executor(
                    None, self.client.make_bucket, self.bucket_name
                )
                print(f"✅ Created MinIO bucket: {self.bucket_name}")
            else:
                print(f"✅ MinIO bucket exists: {self.bucket_name}")

            self._bucket_checked = True

        except S3Error as e:
            print(f"❌ MinIO bucket error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Storage initialization failed: {str(e)}",
            )

    def _ensure_bucket_exists_sync(self):
        """Synchronous version for use in Celery tasks"""
        if self._bucket_checked:
            return

        try:
            # Check if bucket exists
            bucket_exists = self.client.bucket_exists(self.bucket_name)

            if not bucket_exists:
                # Create bucket
                self.client.make_bucket(self.bucket_name)
                print(f"✅ Created MinIO bucket: {self.bucket_name}")
            else:
                print(f"✅ MinIO bucket exists: {self.bucket_name}")

            self._bucket_checked = True

        except S3Error as e:
            print(f"❌ MinIO bucket error: {e}")
            raise Exception(f"Storage initialization failed: {str(e)}")

    async def upload_file(
        self,
        object_name: str,
        data: Union[bytes, BinaryIO],
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        """Upload file to MinIO storage"""
        await self._ensure_bucket_exists()

        try:
            # Convert bytes to BytesIO if needed
            if isinstance(data, bytes):
                data_stream = io.BytesIO(data)
                length = len(data)
            else:
                data_stream = data
                # For file-like objects, seek to end to get size
                data_stream.seek(0, 2)
                length = data_stream.tell()
                data_stream.seek(0)

            # Prepare metadata
            if metadata is None:
                metadata = {}

            # Upload file
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.client.put_object,
                self.bucket_name,
                object_name,
                data_stream,
                length,
                content_type,
                metadata,
            )

            print(f"✅ Uploaded file: {object_name}")
            return object_name

        except S3Error as e:
            print(f"❌ Upload failed for {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}",
            )

    def upload_file_sync(
        self,
        object_name: str,
        data: Union[bytes, BinaryIO],
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        """Synchronous upload for use in Celery tasks"""
        self._ensure_bucket_exists_sync()

        try:
            # Convert bytes to BytesIO if needed
            if isinstance(data, bytes):
                data_stream = io.BytesIO(data)
                length = len(data)
            else:
                data_stream = data
                # For file-like objects, seek to end to get size
                data_stream.seek(0, 2)
                length = data_stream.tell()
                data_stream.seek(0)

            # Prepare metadata
            if metadata is None:
                metadata = {}

            # Upload file synchronously
            result = self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length,
                content_type,
                metadata,
            )

            print(f"✅ Uploaded file: {object_name}")
            return object_name

        except S3Error as e:
            print(f"❌ Upload failed for {object_name}: {e}")
            raise Exception(f"File upload failed: {str(e)}")

    async def get_file_content(self, object_name: str) -> bytes:
        """Get file content from MinIO storage"""
        try:
            loop = asyncio.get_event_loop()

            # Get object
            response = await loop.run_in_executor(
                None, self.client.get_object, self.bucket_name, object_name
            )

            # Read content
            content = response.read()
            response.close()
            response.release_conn()

            return content

        except S3Error as e:
            print(f"❌ Failed to get file {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {object_name}",
            )

    def get_file_content_sync(self, object_name: str) -> bytes:
        """Synchronous get file content for use in Celery tasks"""
        try:
            # Get object synchronously
            response = self.client.get_object(self.bucket_name, object_name)

            # Read content
            content = response.read()
            response.close()
            response.release_conn()

            return content

        except S3Error as e:
            print(f"❌ Failed to get file {object_name}: {e}")
            raise Exception(f"File not found: {object_name}")

    async def get_file_stream(self, object_name: str):
        """Get file stream from MinIO storage"""
        try:
            loop = asyncio.get_event_loop()

            response = await loop.run_in_executor(
                None, self.client.get_object, self.bucket_name, object_name
            )

            return response

        except S3Error as e:
            print(f"❌ Failed to stream file {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {object_name}",
            )

    async def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO storage"""
        try:
            loop = asyncio.get_event_loop()

            await loop.run_in_executor(
                None, self.client.remove_object, self.bucket_name, object_name
            )

            print(f"✅ Deleted file: {object_name}")
            return True

        except S3Error as e:
            print(f"❌ Failed to delete file {object_name}: {e}")
            return False

    def delete_file_sync(self, object_name: str) -> bool:
        """Synchronous delete for use in Celery tasks"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            print(f"✅ Deleted file: {object_name}")
            return True

        except S3Error as e:
            print(f"❌ Failed to delete file {object_name}: {e}")
            return False

    async def file_exists(self, object_name: str) -> bool:
        """Check if file exists in MinIO storage"""
        try:
            loop = asyncio.get_event_loop()

            await loop.run_in_executor(
                None, self.client.stat_object, self.bucket_name, object_name
            )

            return True

        except S3Error:
            return False

    def file_exists_sync(self, object_name: str) -> bool:
        """Synchronous file exists check for use in Celery tasks"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    async def get_file_info(self, object_name: str) -> dict:
        """Get file information from MinIO storage"""
        try:
            loop = asyncio.get_event_loop()

            stat = await loop.run_in_executor(
                None, self.client.stat_object, self.bucket_name, object_name
            )

            return {
                "name": object_name,
                "size": stat.size,
                "etag": stat.etag,
                "last_modified": stat.last_modified.isoformat(),
                "content_type": stat.content_type,
                "metadata": stat.metadata,
            }

        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {object_name}",
            )

    async def get_presigned_url(
        self, object_name: str, expires_in: int = 3600, method: str = "GET"
    ) -> str:
        """Get presigned URL for file access"""
        try:
            loop = asyncio.get_event_loop()

            url = await loop.run_in_executor(
                None,
                self.client.presigned_get_object,
                self.bucket_name,
                object_name,
                timedelta(seconds=expires_in),
            )

            return url

        except S3Error as e:
            print(f"❌ Failed to generate presigned URL for {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate access URL: {str(e)}",
            )

    async def get_upload_url(self, object_name: str, expires_in: int = 3600) -> str:
        """Get presigned URL for file upload"""
        try:
            loop = asyncio.get_event_loop()

            url = await loop.run_in_executor(
                None,
                self.client.presigned_put_object,
                self.bucket_name,
                object_name,
                timedelta(seconds=expires_in),
            )

            return url

        except S3Error as e:
            print(f"❌ Failed to generate upload URL for {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate upload URL: {str(e)}",
            )

    async def list_files(
        self, prefix: str = "", recursive: bool = True, max_keys: int = 1000
    ) -> list:
        """List files in MinIO storage"""
        try:
            loop = asyncio.get_event_loop()

            objects = await loop.run_in_executor(
                None,
                lambda: list(
                    self.client.list_objects(
                        self.bucket_name, prefix=prefix, recursive=recursive
                    )
                ),
            )

            # Limit results
            objects = objects[:max_keys]

            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": (
                        obj.last_modified.isoformat() if obj.last_modified else None
                    ),
                    "etag": obj.etag,
                    "is_dir": obj.is_dir,
                }
                for obj in objects
            ]

        except S3Error as e:
            print(f"❌ Failed to list files with prefix {prefix}: {e}")
            return []

    async def copy_file(self, source_object: str, destination_object: str) -> bool:
        """Copy file within MinIO storage"""
        try:
            from minio.commonconfig import CopySource

            loop = asyncio.get_event_loop()

            await loop.run_in_executor(
                None,
                self.client.copy_object,
                self.bucket_name,
                destination_object,
                CopySource(self.bucket_name, source_object),
            )

            print(f"✅ Copied file: {source_object} -> {destination_object}")
            return True

        except S3Error as e:
            print(f"❌ Failed to copy file {source_object}: {e}")
            return False

    async def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        try:
            files = await self.list_files(recursive=True, max_keys=10000)

            total_size = sum(file["size"] for file in files)
            total_files = len(files)

            # Group by file type
            file_types = {}
            for file in files:
                ext = (
                    file["name"].split(".")[-1].lower()
                    if "." in file["name"]
                    else "unknown"
                )
                if ext not in file_types:
                    file_types[ext] = {"count": 0, "size": 0}
                file_types[ext]["count"] += 1
                file_types[ext]["size"] += file["size"]

            return {
                "bucket_name": self.bucket_name,
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_types": file_types,
                "storage_endpoint": settings.MINIO_ENDPOINT,
            }

        except Exception as e:
            return {
                "error": f"Failed to get storage stats: {str(e)}",
                "bucket_name": self.bucket_name,
            }

    async def health_check(self) -> dict:
        """Check MinIO service health"""
        try:
            # Try to list buckets to test connection
            loop = asyncio.get_event_loop()

            buckets = await loop.run_in_executor(None, self.client.list_buckets)

            bucket_names = [bucket.name for bucket in buckets]

            return {
                "status": "healthy",
                "service": "MinIO",
                "endpoint": settings.MINIO_ENDPOINT,
                "bucket_exists": self.bucket_name in bucket_names,
                "buckets": bucket_names,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "MinIO",
                "endpoint": settings.MINIO_ENDPOINT,
                "error": str(e),
            }


# Chunked upload support for large files
class ChunkedUploadManager:
    """Manager for chunked file uploads"""

    def __init__(self, minio_service: MinIOService):
        self.minio = minio_service
        self.upload_sessions = {}

    async def start_chunked_upload(
        self, object_name: str, total_size: int, chunk_size: int = 8192
    ) -> str:
        """Start a chunked upload session"""
        upload_id = str(id(object_name))  # Simple ID generation

        self.upload_sessions[upload_id] = {
            "object_name": object_name,
            "total_size": total_size,
            "chunk_size": chunk_size,
            "uploaded_chunks": [],
            "bytes_uploaded": 0,
        }

        return upload_id

    async def upload_chunk(
        self, upload_id: str, chunk_data: bytes, chunk_number: int
    ) -> dict:
        """Upload a chunk of data"""
        if upload_id not in self.upload_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Upload session not found"
            )

        session = self.upload_sessions[upload_id]

        # Store chunk (in a real implementation, you'd use MinIO multipart upload)
        session["uploaded_chunks"].append(
            {"number": chunk_number, "data": chunk_data, "size": len(chunk_data)}
        )

        session["bytes_uploaded"] += len(chunk_data)

        progress = (session["bytes_uploaded"] / session["total_size"]) * 100

        return {
            "upload_id": upload_id,
            "chunk_number": chunk_number,
            "bytes_uploaded": session["bytes_uploaded"],
            "total_size": session["total_size"],
            "progress": progress,
            "is_complete": progress >= 100,
        }

    async def complete_chunked_upload(self, upload_id: str) -> str:
        """Complete chunked upload and assemble file"""
        if upload_id not in self.upload_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Upload session not found"
            )

        session = self.upload_sessions[upload_id]

        # Combine all chunks
        chunks = sorted(session["uploaded_chunks"], key=lambda x: x["number"])
        combined_data = b"".join(chunk["data"] for chunk in chunks)

        # Upload combined file
        await self.minio.upload_file(
            session["object_name"],
            combined_data,
            content_type="application/octet-stream",
        )

        # Cleanup session
        del self.upload_sessions[upload_id]

        return session["object_name"]
