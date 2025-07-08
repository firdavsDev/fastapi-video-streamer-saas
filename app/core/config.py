"""
🎬 Video Streaming Backend Configuration
Core application settings and environment variables
"""

from functools import lru_cache
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # 🌐 Application Settings
    APP_NAME: str = "Video Streaming Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # 🔒 Security Settings
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this-too"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # 📊 Database Configuration
    DATABASE_URL: str = "sqlite:///./video_streaming.db"

    # 🔗 API Configuration
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 📁 File Storage Settings
    MAX_UPLOAD_SIZE: int = 209715200  # 200MB in bytes
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    UPLOAD_CHUNK_SIZE: int = 8192  # 8KB chunks for streaming

    # 🗄️ MinIO Configuration
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "video-streaming"
    MINIO_SECURE: bool = False

    # AWS S3 Configuration (alternative to MinIO)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None

    # 🔄 Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"

    # 🚀 Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # 📊 Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_LOGGING: bool = True
    LOG_FILE: str = "logs/video_streaming.log"

    # 🎯 Video Processing Settings
    ENABLE_VIDEO_THUMBNAILS: bool = True
    THUMBNAIL_QUALITY: int = 80
    ENABLE_VIDEO_TRANSCODING: bool = False
    SUPPORTED_VIDEO_FORMATS: List[str] = ["mp4", "webm", "mov"]

    # 🔐 Admin Authentication
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    # 🌐 External Services
    ENABLE_ANALYTICS: bool = False
    ANALYTICS_API_KEY: str = ""

    # 📱 Frontend Settings
    FRONTEND_URL: str = "http://localhost:3000"
    ENABLE_CORS: bool = True

    # 🐳 Docker Configuration
    POSTGRES_DB: str = "video_streaming"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"

    # 🏥 Health Check Settings
    HEALTH_CHECK_INTERVAL: int = 30
    ENABLE_HEALTH_CHECKS: bool = True

    # 🎥 Video Streaming Settings
    ENABLE_VIDEO_RESUME: bool = True
    DEFAULT_VIDEO_QUALITY: str = "720p"
    ENABLE_ADAPTIVE_STREAMING: bool = False
    STREAMING_CHUNK_SIZE: int = 1048576  # 1MB

    # 📈 Performance Settings
    MAX_CONCURRENT_UPLOADS: int = 5
    UPLOAD_TIMEOUT: int = 300  # 5 minutes
    STREAM_BUFFER_SIZE: int = 8192
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600  # 1 hour

    # 🛡️ Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # per minute

    # 🔍 Search & Indexing
    ENABLE_VIDEO_SEARCH: bool = True
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # 📧 Email Settings
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    # 🎨 UI Customization
    BRAND_NAME: str = "Your Video Platform"
    BRAND_LOGO_URL: str = ""
    CUSTOM_CSS_URL: str = ""

    # 🔧 Development Settings
    AUTO_RELOAD: bool = True
    ENABLE_DEBUG_TOOLBAR: bool = True
    ENABLE_PROFILING: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # << qo‘shildi

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_url_async(self) -> str:
        """Get async database URL"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self.DATABASE_URL

    @property
    def allowed_hosts(self) -> List[str]:
        """Get allowed hosts for CORS"""
        return [str(origin) for origin in self.CORS_ORIGINS]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
