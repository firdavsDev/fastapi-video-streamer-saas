"""
📁 Local Storage Service
Alternative storage implementation for local development
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO, Optional, Union

from fastapi import HTTPException, status

from app.core.config import settings


class LocalStorageService:
    """Local filesystem storage service for development"""

    def __init__(self, base_path: str = "uploads"):
        """Initialize local storage service"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.base_path / "videos").mkdir(exist_ok=True)
        (self.base_path / "thumbnails").mkdir(exist_ok=True)
        (self.base_path / "temp").mkdir(exist_ok=True)

    async def upload_file(
        self,
        object_name: str,
        data: Union[bytes, BinaryIO],
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        """Upload file to local storage"""
        try:
            file_path = self.base_path / object_name

            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            if isinstance(data, bytes):
                with open(file_path, "wb") as f:
                    f.write(data)
            else:
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(data, f)

            # Save metadata if provided
            if metadata:
                metadata_path = file_path.with_suffix(".meta")
                import json

                with open(metadata_path, "w") as f:
                    json.dump(
                        {
                            **metadata,
                            "content_type": content_type,
                            "uploaded_at": datetime.utcnow().isoformat(),
                            "size": file_path.stat().st_size,
                        },
                        f,
                        indent=2,
                    )

            print(f"✅ Uploaded file to local storage: {object_name}")
            return str(file_path)

        except Exception as e:
            print(f"❌ Local upload failed for {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}",
            )

    async def get_file_content(self, object_name: str) -> bytes:
        """Get file content from local storage"""
        try:
            file_path = self.base_path / object_name

            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File not found: {object_name}",
                )

            with open(file_path, "rb") as f:
                return f.read()

        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Failed to get local file {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}",
            )

    async def get_file_stream(self, object_name: str):
        """Get file stream from local storage"""
        try:
            file_path = self.base_path / object_name

            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File not found: {object_name}",
                )

            return open(file_path, "rb")

        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Failed to stream local file {object_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to stream file: {str(e)}",
            )

    async def delete_file(self, object_name: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = self.base_path / object_name
            metadata_path = file_path.with_suffix(".meta")

            # Delete main file
            if file_path.exists():
                file_path.unlink()
                print(f"✅ Deleted local file: {object_name}")

            # Delete metadata file
            if metadata_path.exists():
                metadata_path.unlink()

            return True

        except Exception as e:
            print(f"❌ Failed to delete local file {object_name}: {e}")
            return False

    async def file_exists(self, object_name: str) -> bool:
        """Check if file exists in local storage"""
        file_path = self.base_path / object_name
        return file_path.exists()

    async def get_file_info(self, object_name: str) -> dict:
        """Get file information from local storage"""
        try:
            file_path = self.base_path / object_name
            metadata_path = file_path.with_suffix(".meta")

            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File not found: {object_name}",
                )

            stat = file_path.stat()

            # Load metadata if available
            metadata = {}
            if metadata_path.exists():
                import json

                with open(metadata_path, "r") as f:
                    metadata = json.load(f)

            return {
                "name": object_name,
                "size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "content_type": metadata.get(
                    "content_type", "application/octet-stream"
                ),
                "metadata": metadata,
                "path": str(file_path),
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file info: {str(e)}",
            )

    async def get_presigned_url(
        self, object_name: str, expires_in: int = 3600, method: str = "GET"
    ) -> str:
        """Get presigned URL for file access (local implementation)"""
        # For local storage, return a direct file path or localhost URL
        file_path = self.base_path / object_name

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {object_name}",
            )

        # Return localhost URL that your API can serve
        return f"http://localhost:8000/api/v1/files/{object_name}"

    async def list_files(
        self, prefix: str = "", recursive: bool = True, max_keys: int = 1000
    ) -> list:
        """List files in local storage"""
        try:
            files = []
            search_path = self.base_path / prefix if prefix else self.base_path

            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"

            for file_path in search_path.glob(pattern):
                if file_path.is_file() and not file_path.name.endswith(".meta"):
                    relative_path = file_path.relative_to(self.base_path)
                    stat = file_path.stat()

                    files.append(
                        {
                            "name": str(relative_path),
                            "size": stat.st_size,
                            "last_modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "is_dir": False,
                        }
                    )

                    if len(files) >= max_keys:
                        break

            return files

        except Exception as e:
            print(f"❌ Failed to list local files with prefix {prefix}: {e}")
            return []

    async def copy_file(self, source_object: str, destination_object: str) -> bool:
        """Copy file within local storage"""
        try:
            source_path = self.base_path / source_object
            dest_path = self.base_path / destination_object

            if not source_path.exists():
                return False

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_path, dest_path)

            # Copy metadata if exists
            source_meta = source_path.with_suffix(".meta")
            if source_meta.exists():
                dest_meta = dest_path.with_suffix(".meta")
                shutil.copy2(source_meta, dest_meta)

            print(f"✅ Copied local file: {source_object} -> {destination_object}")
            return True

        except Exception as e:
            print(f"❌ Failed to copy local file {source_object}: {e}")
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
                ext = Path(file["name"]).suffix.lower() or "no_extension"
                if ext not in file_types:
                    file_types[ext] = {"count": 0, "size": 0}
                file_types[ext]["count"] += 1
                file_types[ext]["size"] += file["size"]

            return {
                "storage_type": "local",
                "base_path": str(self.base_path),
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_types": file_types,
                "available_space_mb": self._get_available_space(),
            }

        except Exception as e:
            return {
                "error": f"Failed to get storage stats: {str(e)}",
                "storage_type": "local",
                "base_path": str(self.base_path),
            }

    def _get_available_space(self) -> float:
        """Get available disk space in MB"""
        try:
            stat = shutil.disk_usage(self.base_path)
            return round(stat.free / (1024 * 1024), 2)
        except:
            return 0.0

    async def health_check(self) -> dict:
        """Check local storage health"""
        try:
            # Test write/read/delete
            test_file = self.base_path / "health_check.txt"
            test_content = f"Health check at {datetime.utcnow().isoformat()}"

            # Write test
            test_file.write_text(test_content)

            # Read test
            read_content = test_file.read_text()

            # Delete test
            test_file.unlink()

            # Check if content matches
            if read_content == test_content:
                return {
                    "status": "healthy",
                    "storage_type": "local",
                    "base_path": str(self.base_path),
                    "writable": True,
                    "readable": True,
                    "available_space_mb": self._get_available_space(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "storage_type": "local",
                    "error": "Content mismatch in read/write test",
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "storage_type": "local",
                "error": str(e),
                "base_path": str(self.base_path),
            }

    async def cleanup_temp_files(self, older_than_hours: int = 24) -> dict:
        """Clean up temporary files older than specified hours"""
        try:
            temp_path = self.base_path / "temp"
            if not temp_path.exists():
                return {"cleaned": 0, "errors": []}

            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            cleaned = 0
            errors = []

            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            file_path.unlink()
                            cleaned += 1
                    except Exception as e:
                        errors.append(f"Failed to delete {file_path}: {str(e)}")

            return {
                "cleaned": cleaned,
                "errors": errors,
                "cutoff_time": cutoff_time.isoformat(),
            }

        except Exception as e:
            return {"cleaned": 0, "errors": [f"Cleanup failed: {str(e)}"]}
