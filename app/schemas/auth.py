from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
