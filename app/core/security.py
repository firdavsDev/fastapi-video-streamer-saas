"""
🔒 Video Streaming Backend Security Module
JWT authentication, password hashing, and security utilities
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 🔐 Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Security utilities for authentication and authorization"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        subject: Union[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        subject: Union[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def create_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate a secure filename"""
        import os
        import uuid

        # Get file extension
        _, ext = os.path.splitext(original_filename)

        # Generate UUID-based filename
        secure_name = str(uuid.uuid4())

        return f"{secure_name}{ext}"

    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: list) -> bool:
        """Validate file type by extension"""
        import os

        _, ext = os.path.splitext(filename.lower())
        return ext in [e.lower() for e in allowed_extensions]

    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> bool:
        """Validate file size"""
        return file_size <= max_size

    @staticmethod
    def create_presigned_url_token(
        video_id: str,
        user_id: Optional[str] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create presigned URL token for video access"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour default

        to_encode = {
            "exp": expire,
            "video_id": video_id,
            "user_id": user_id,
            "type": "video_access",
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_presigned_url_token(token: str) -> Dict[str, Any]:
        """Verify presigned URL token"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get("type") != "video_access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired video access token",
            )


# 🛡️ Rate Limiting
class RateLimiter:
    """Rate limiting utilities"""

    def __init__(self):
        self.requests = {}

    def is_allowed(self, identifier: str, max_requests: int, window: int) -> bool:
        """Check if request is allowed within rate limit"""
        now = datetime.utcnow()

        if identifier not in self.requests:
            self.requests[identifier] = []

        # Clean old requests
        self.requests[identifier] = [
            req_time
            for req_time in self.requests[identifier]
            if (now - req_time).total_seconds() < window
        ]

        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

    def get_remaining_requests(self, identifier: str, max_requests: int) -> int:
        """Get remaining requests for identifier"""
        if identifier not in self.requests:
            return max_requests

        return max(0, max_requests - len(self.requests[identifier]))


# 🔑 Permission System
class PermissionManager:
    """Permission management system"""

    # Permission levels
    GUEST = 0
    USER = 1
    ADMIN = 2
    SUPER_ADMIN = 3

    PERMISSION_NAMES = {
        GUEST: "guest",
        USER: "user",
        ADMIN: "admin",
        SUPER_ADMIN: "super_admin",
    }

    @staticmethod
    def has_permission(user_level: int, required_level: int) -> bool:
        """Check if user has required permission level"""
        return user_level >= required_level

    @staticmethod
    def get_permission_name(level: int) -> str:
        """Get permission name from level"""
        return PermissionManager.PERMISSION_NAMES.get(level, "unknown")

    @staticmethod
    def can_upload_video(user_level: int) -> bool:
        """Check if user can upload videos"""
        return user_level >= PermissionManager.ADMIN

    @staticmethod
    def can_delete_video(user_level: int) -> bool:
        """Check if user can delete videos"""
        return user_level >= PermissionManager.ADMIN

    @staticmethod
    def can_manage_users(user_level: int) -> bool:
        """Check if user can manage other users"""
        return user_level >= PermissionManager.SUPER_ADMIN


# 🔐 Security Headers
class SecurityHeaders:
    """Security headers configuration"""

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


# 🔒 Input Validation
class InputValidator:
    """Input validation utilities"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        import re

        result = {"is_valid": True, "errors": [], "score": 0}

        # Length check
        if len(password) < 8:
            result["errors"].append("Password must be at least 8 characters long")
            result["is_valid"] = False
        else:
            result["score"] += 1

        # Uppercase check
        if not re.search(r"[A-Z]", password):
            result["errors"].append(
                "Password must contain at least one uppercase letter"
            )
            result["is_valid"] = False
        else:
            result["score"] += 1

        # Lowercase check
        if not re.search(r"[a-z]", password):
            result["errors"].append(
                "Password must contain at least one lowercase letter"
            )
            result["is_valid"] = False
        else:
            result["score"] += 1

        # Number check
        if not re.search(r"\d", password):
            result["errors"].append("Password must contain at least one number")
            result["is_valid"] = False
        else:
            result["score"] += 1

        # Special character check
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["errors"].append(
                "Password must contain at least one special character"
            )
            result["is_valid"] = False
        else:
            result["score"] += 1

        return result

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for security"""
        import os
        import re

        # Remove path separators
        filename = os.path.basename(filename)

        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[: 255 - len(ext)] + ext

        return filename

    @staticmethod
    def validate_video_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate video metadata"""
        result = {"is_valid": True, "errors": []}

        # Check required fields
        required_fields = ["title", "duration"]
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                result["errors"].append(f"Missing required field: {field}")
                result["is_valid"] = False

        # Validate title length
        if "title" in metadata and len(metadata["title"]) > 200:
            result["errors"].append("Title must be less than 200 characters")
            result["is_valid"] = False

        # Validate duration
        if "duration" in metadata:
            try:
                duration = float(metadata["duration"])
                if duration <= 0:
                    result["errors"].append("Duration must be positive")
                    result["is_valid"] = False
                elif duration > 7200:  # 2 hours max
                    result["errors"].append("Video duration cannot exceed 2 hours")
                    result["is_valid"] = False
            except (ValueError, TypeError):
                result["errors"].append("Invalid duration format")
                result["is_valid"] = False

        return result


# 🎯 Security Instance
security_manager = SecurityManager()
rate_limiter = RateLimiter()
permission_manager = PermissionManager()
input_validator = InputValidator()
