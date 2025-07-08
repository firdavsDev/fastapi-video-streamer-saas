"""
🔐 Authentication API
JWT-based authentication for admin users
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.core.security import PermissionManager, SecurityManager
from app.dependencys.auth import get_current_admin, get_current_user
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    UserInfo,
)
from app.services.auth import ADMIN_USERS, AuthService

# Initialize router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

# Security scheme
security = HTTPBearer()


# Authentication endpoints
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login with username and password"""

    # Rate limiting check (simplified)
    # In production, implement proper rate limiting

    # Authenticate user
    user = AuthService.authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    tokens = AuthService.create_tokens(user)

    return LoginResponse(**tokens)


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""

    try:
        # Verify refresh token
        payload = SecurityManager.verify_token(refresh_data.refresh_token)
        username = payload.get("sub")
        token_type = payload.get("type")

        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Get user
        user = AuthService.get_user_by_username(username)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new tokens
        tokens = AuthService.create_tokens(user)
        return LoginResponse(**tokens)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {str(e)}",
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (in a real app, you'd blacklist the token)"""
    return {"message": "Successfully logged out", "user": current_user["username"]}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserInfo(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest, current_user: dict = Depends(get_current_user)
):
    """Change user password"""

    # Verify current password
    if not SecurityManager.verify_password(
        password_data.current_password, current_user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate new password
    validation = SecurityManager.input_validator.validate_password_strength(
        password_data.new_password
    )

    if not validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet requirements",
                "errors": validation["errors"],
            },
        )

    # Update password (in memory for this demo)
    new_password_hash = SecurityManager.get_password_hash(password_data.new_password)
    ADMIN_USERS[current_user["username"]]["password_hash"] = new_password_hash

    return {"message": "Password changed successfully"}


@router.post("/validate-token")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """Validate current token"""
    return {
        "valid": True,
        "user": {
            "username": current_user["username"],
            "role": current_user["role"],
            "permission_level": current_user["permission_level"],
        },
    }


# Admin-only endpoints
@router.get("/users")
async def list_users(current_admin: dict = Depends(get_current_admin)):
    """List all users (admin only)"""
    users = []
    for username, user_data in ADMIN_USERS.items():
        users.append(
            {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "role": user_data["role"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"].isoformat(),
            }
        )

    return {"users": users}


@router.post("/users/{username}/toggle-status")
async def toggle_user_status(
    username: str, current_admin: dict = Depends(get_current_admin)
):
    """Toggle user active status (admin only)"""

    if username not in ADMIN_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Don't allow admin to deactivate themselves
    if username == current_admin["username"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own status",
        )

    # Toggle status
    ADMIN_USERS[username]["is_active"] = not ADMIN_USERS[username]["is_active"]
    new_status = "activated" if ADMIN_USERS[username]["is_active"] else "deactivated"

    return {
        "message": f"User {username} has been {new_status}",
        "user": username,
        "is_active": ADMIN_USERS[username]["is_active"],
    }


# Security utilities
@router.get("/permissions")
async def get_user_permissions(current_user: dict = Depends(get_current_user)):
    """Get current user permissions"""
    permission_level = current_user["permission_level"]

    return {
        "user": current_user["username"],
        "permission_level": permission_level,
        "permission_name": PermissionManager.get_permission_name(permission_level),
        "can_upload_videos": PermissionManager.can_upload_video(permission_level),
        "can_delete_videos": PermissionManager.can_delete_video(permission_level),
        "can_manage_users": PermissionManager.can_manage_users(permission_level),
    }


@router.get("/session-info")
async def get_session_info(current_user: dict = Depends(get_current_user)):
    """Get current session information"""
    return {
        "user": {
            "username": current_user["username"],
            "role": current_user["role"],
            "email": current_user["email"],
        },
        "session": {
            "authenticated": True,
            "login_time": datetime.utcnow().isoformat(),
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
        "capabilities": {
            "video_upload": True,
            "video_management": True,
            "analytics_access": True,
            "user_management": PermissionManager.can_manage_users(
                current_user["permission_level"]
            ),
        },
    }
