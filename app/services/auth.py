from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.security import PermissionManager, SecurityManager

# Simple in-memory user store (replace with database in production)
ADMIN_USERS = {
    "admin": {
        "id": "admin-001",
        "username": "admin",
        "email": settings.ADMIN_EMAIL,
        "password_hash": SecurityManager.get_password_hash(settings.ADMIN_PASSWORD),
        "role": "admin",
        "permission_level": PermissionManager.ADMIN,
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
}


class AuthService:
    """Authentication service"""

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password"""
        user = ADMIN_USERS.get(username)
        if not user:
            return None

        if not SecurityManager.verify_password(password, user["password_hash"]):
            return None

        if not user["is_active"]:
            return None

        return user

    @staticmethod
    def get_user_by_username(username: str) -> Optional[dict]:
        """Get user by username"""
        return ADMIN_USERS.get(username)

    @staticmethod
    def create_tokens(user: dict) -> dict:
        """Create access and refresh tokens"""
        # Create access token
        access_token = SecurityManager.create_access_token(subject=user["username"])

        # Create refresh token
        refresh_token = SecurityManager.create_refresh_token(subject=user["username"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_info": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "permission_level": user["permission_level"],
            },
        }
