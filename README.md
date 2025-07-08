# 🎬 Video Streaming Backend with FastAPI

A secure, scalable video streaming service built with FastAPI, Celery, and MinIO for custom video hosting and streaming.

## 📁 Project Structure

```bash
.
├── .env
├── .env.example
├── .gitignore
├── app
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── videos.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   └── video.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── minio_service.py
│   │   └── video_service.py
│   ├── storage
│   │   ├── __init__.py
│   │   └── local_storage.p
│   └── workers
│       ├── __init__.py
│       └── video_worker.py
├── celery_worker
│   ├── __init__.py
│   ├── tasks.py
│   └── worker.py
├── docker
│   ├── docker-compose.yml
│   └── Dockerfile
├── frontend
│   ├── video-player.html
│   └── video-player.js
├── README.md
└── requirements.txt
```

## 🚀 Quick Start

### 1. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
# Edit .env with your specific configuration
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Services with Docker

```bash
# Start all services (FastAPI, Celery, MinIO, Redis)
docker-compose -f docker/docker-compose.yml up --build --remove-orphans

# Or run locally for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access Services

- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin/password123)
- **Video Player Example**: Open `frontend/video-player.html`

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - Admin login
- `POST /auth/refresh` - Refresh JWT token

### Video Management
- `GET /videos/` - List all videos (admin only)
- `POST /videos/upload` - Upload new video (admin only)
- `GET /videos/{video_id}/status` - Check upload status
- `GET /videos/{video_id}/stream` - Stream video (blob response)
- `DELETE /videos/{video_id}` - Delete video (admin only)

### Video Streaming
- `GET /videos/{video_id}/stream` - Secure video streaming endpoint
- `GET /videos/{video_id}/thumbnail` - Get video thumbnail
- `POST /videos/{video_id}/progress` - Save video progress

## 📊 Video Upload Flow

1. **Admin uploads video** via `/videos/upload`
2. **Celery task** processes upload asynchronously
3. **Status tracking** via `/videos/{video_id}/status`
4. **Secure streaming** via `/videos/{video_id}/stream`

## 🔒 Security Features

- **JWT Authentication** for admin operations
- **Blob streaming** prevents direct file access
- **Presigned URLs** for temporary access
- **Rate limiting** on streaming endpoints
- **File validation** (size, format, duration)

## 🎯 Video Resume Feature

Videos automatically resume from the last watched position using:
- **Frontend localStorage** for position tracking
- **Server-side progress** API for cross-device sync
- **Blob streaming** with range requests

## 📱 Frontend Integration

```javascript
// Example: Streaming video in React
const VideoPlayer = ({ videoId }) => {
  const videoRef = useRef(null);
  
  useEffect(() => {
    const streamVideo = async () => {
      const response = await fetch(`/videos/${videoId}/stream`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const blob = await response.blob();
      const videoUrl = URL.createObjectURL(blob);
      
      if (videoRef.current) {
        videoRef.current.src = videoUrl;
        // Resume from saved position
        const savedTime = localStorage.getItem(`video_${videoId}_time`);
        if (savedTime) {
          videoRef.current.currentTime = parseFloat(savedTime);
        }
      }
    };
    
    streamVideo();
  }, [videoId]);
  
  return (
    <video 
      ref={videoRef}
      controls
      onTimeUpdate={(e) => {
        // Save progress
        localStorage.setItem(`video_${videoId}_time`, e.target.currentTime);
      }}
    />
  );
};
```

## 🐳 Docker Services

The docker-compose setup includes:
- **FastAPI app** (port 8000)
- **Celery worker** for background tasks
- **Redis** for Celery broker
- **MinIO** for object storage (port 9000/9001)
- **PostgreSQL** for production database

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
alembic upgrade head
```

### Monitoring
- **Celery Flower**: http://localhost:5555
- **MinIO Metrics**: Available via MinIO console

## 📈 Production Considerations

- Replace SQLite with PostgreSQL
- Use AWS S3 instead of MinIO
- Implement CDN for video delivery
- Add video transcoding pipeline
- Set up monitoring and logging
- Configure SSL/TLS certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.