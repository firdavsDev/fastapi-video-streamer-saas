from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import PermissionManager, SecurityManager
from app.services.auth import ADMIN_USERS, AuthService

# Security scheme
security = HTTPBearer()


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Get current authenticated user"""
    try:
        # Verify token
        payload = SecurityManager.verify_token(credentials.credentials)
        username = payload.get("sub")
        token_type = payload.get("type", "access")

        if username is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user
        user = AuthService.get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency to check admin permissions
async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Ensure current user has admin permissions"""
    if not PermissionManager.has_permission(
        current_user["permission_level"], PermissionManager.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
