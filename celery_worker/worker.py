"""
🔄 Celery Worker Configuration
Main worker setup and configuration
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from celery_worker.tasks import celery_app

# Worker configuration
celery_app.conf.update(
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    worker_disable_rate_limits=False,
    # Task settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    # Routing
    task_routes={
        "process_video_upload": {"queue": "video_processing"},
        "generate_video_thumbnail": {"queue": "thumbnails"},
        "cleanup_temp_files": {"queue": "cleanup"},
        "process_video_analytics": {"queue": "analytics"},
        "health_check_videos": {"queue": "health"},
        "periodic_cleanup": {"queue": "maintenance"},
    },
    # Queue configuration
    task_default_queue="default",
    task_queue_max_priority=10,
    task_default_priority=5,
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    # Error handling
    task_annotations={
        "*": {"rate_limit": "100/m"},
        "process_video_upload": {
            "rate_limit": "10/m",
            "time_limit": 1800,  # 30 minutes
            "soft_time_limit": 1500,  # 25 minutes
            "retry_kwargs": {"max_retries": 3, "countdown": 60},
        },
        "generate_video_thumbnail": {
            "rate_limit": "20/m",
            "time_limit": 300,  # 5 minutes
            "retry_kwargs": {"max_retries": 2, "countdown": 30},
        },
    },
)


def setup_logging():
    """Setup logging for worker"""
    import logging

    from loguru import logger

    # Configure loguru
    logger.add(
        "logs/celery_worker.log",
        rotation="1 day",
        retention="7 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    )

    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0)


def create_directories():
    """Create necessary directories"""
    directories = ["logs", "tmp", "uploads"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Setup
if __name__ == "__main__":
    setup_logging()
    create_directories()

    # Start worker
    celery_app.start()


# Export the worker instance for Celery CLI
worker = celery_app
