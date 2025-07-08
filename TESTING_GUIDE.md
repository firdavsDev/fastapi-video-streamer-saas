# 🧪 API Testing Guide

Complete guide for testing the Video Streaming Backend API endpoints using Postman, Swagger, or curl.

## 🚀 Quick Start

### 1. Start the Services

```bash
# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# Or start locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info**: http://localhost:8000/api/v1/info

## 🔍 Health Check Endpoints

### System Health
```bash
curl -X GET "http://localhost:8000/health"
```

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": 1640995200.123,
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": {"status": "healthy"},
    "storage": {"status": "healthy"}
  }
}
```

### Database Health
```bash
curl -X GET "http://localhost:8000/health/database"
```

### Storage Health
```bash
curl -X GET "http://localhost:8000/health/storage"
```

## 🔐 Authentication Endpoints

### 1. Login (Get JWT Token)

**POST** `/api/v1/auth/login`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Expected Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_info": {
    "id": "admin-001",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "permission_level": 2
  }
}
```

### 2. Get Current User Info

**GET** `/api/v1/auth/me`

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Refresh Token

**POST** `/api/v1/auth/refresh`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## 🎬 Video Management Endpoints

> **Note**: All video endpoints require authentication. Include the `Authorization: Bearer YOUR_TOKEN` header.

### 1. List Videos

**GET** `/api/v1/videos/`

```bash
curl -X GET "http://localhost:8000/api/v1/videos/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Query Parameters:
- `skip`: Number of videos to skip (default: 0)
- `limit`: Number of videos to return (default: 50, max: 100)
- `status`: Filter by status (`pending`, `uploading`, `processing`, `completed`, `failed`)
- `search`: Search in title and description

### 2. Get Single Video

**GET** `/api/v1/videos/{video_id}`

```bash
curl -X GET "http://localhost:8000/api/v1/videos/VIDEO_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Upload Video

**POST** `/api/v1/videos/upload`

```bash
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "title=My Test Video" \
  -F "description=This is a test video upload" \
  -F "file=@/path/to/video.mp4"
```

Expected Response:
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_session_id": "session_123",
  "status": "uploading",
  "message": "Video upload started. Task ID: task_456"
}
```

### 4. Check Upload Status

**GET** `/api/v1/videos/{video_id}/status`

```bash
curl -X GET "http://localhost:8000/api/v1/videos/VIDEO_ID/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected Response:
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "processing_progress": 100,
  "error_message": null,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:05:30Z",
  "uploaded_at": "2024-01-15T10:01:15Z",
  "processed_at": "2024-01-15T10:05:30Z"
}
```

### 5. Delete Video

**DELETE** `/api/v1/videos/{video_id}`

```bash
curl -X DELETE "http://localhost:8000/api/v1/videos/VIDEO_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
