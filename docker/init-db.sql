-- 🎬 Video Streaming Backend Database Initialization
-- Creates database and basic setup for PostgreSQL

-- Create database (if not exists)
-- Note: This runs in the postgres database by default

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create video_streaming database if it doesn't exist
SELECT 'CREATE DATABASE video_streaming'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'video_streaming')\gexec

-- Connect to video_streaming database
\c video_streaming;

-- Create extensions in the target database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance (these will be created by SQLAlchemy too)
-- But having them here ensures they exist

-- Note: Tables will be created automatically by SQLAlchemy
-- This script is mainly for extensions and initial setup

-- Insert default admin user (will be handled by the application)
-- The application will create tables and default data

-- Performance tuning
-- Increase work_mem for this database
ALTER DATABASE video_streaming SET work_mem = '256MB';
ALTER DATABASE video_streaming SET maintenance_work_mem = '512MB';
ALTER DATABASE video_streaming SET effective_cache_size = '2GB';

-- Enable logging for slow queries
ALTER DATABASE video_streaming SET log_min_duration_statement = '1000';

-- Create schema for application (optional, using default public schema)
-- CREATE SCHEMA IF NOT EXISTS video_streaming;

-- Set default permissions
-- GRANT ALL PRIVILEGES ON DATABASE video_streaming TO postgres;

COMMENT ON DATABASE video_streaming IS 'Video Streaming Backend Database - Stores video metadata, user sessions, and analytics';

-- Create custom types that might be useful
DO $$ 
BEGIN
    -- Video status enum (SQLAlchemy will also create this)
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'video_status_enum') THEN
        CREATE TYPE video_status_enum AS ENUM (
            'pending',
            'uploading', 
            'processing',
            'completed',
            'failed',
            'deleted'
        );
    END IF;
    
    -- Video quality enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'video_quality_enum') THEN
        CREATE TYPE video_quality_enum AS ENUM (
            '240p',
            '360p',
            '480p',
            '720p',
            '1080p',
            '1440p',
            '2160p'
        );
    END IF;
END $$;

-- Create utility functions

-- Function to generate video thumbnails path
CREATE OR REPLACE FUNCTION generate_thumbnail_path(video_id TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN 'thumbnails/' || video_id || '/thumbnail_' || video_id || '.jpg';
END;
$$ LANGUAGE plpgsql;

-- Function to calculate completion percentage
CREATE OR REPLACE FUNCTION calculate_completion_percentage(curr_time FLOAT, total_duration FLOAT)
RETURNS FLOAT AS $$
BEGIN
    IF total_duration IS NULL OR total_duration <= 0 THEN
        RETURN 0;
    END IF;
    RETURN LEAST(100.0, (curr_time / total_duration) * 100.0);
END;
$$ LANGUAGE plpgsql;

-- Function to format duration as HH:MM:SS
CREATE OR REPLACE FUNCTION format_duration(duration_seconds FLOAT)
RETURNS TEXT AS $$
DECLARE
    hours INTEGER;
    minutes INTEGER;
    seconds INTEGER;
BEGIN
    IF duration_seconds IS NULL THEN
        RETURN '00:00:00';
    END IF;
    
    hours := FLOOR(duration_seconds / 3600);
    minutes := FLOOR((duration_seconds % 3600) / 60);
    seconds := FLOOR(duration_seconds % 60);
    
    RETURN LPAD(hours::TEXT, 2, '0') || ':' || 
           LPAD(minutes::TEXT, 2, '0') || ':' || 
           LPAD(seconds::TEXT, 2, '0');
END;
$$ LANGUAGE plpgsql;

-- Create indexes that will help with common queries
-- Note: These will be created after tables exist, so we'll do this in a function

CREATE OR REPLACE FUNCTION create_performance_indexes()
RETURNS VOID AS $$
BEGIN
    -- Check if tables exist before creating indexes
    
    -- Videos table indexes
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'videos') THEN
        CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
        CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_videos_title_search ON videos USING gin(title gin_trgm_ops);
        CREATE INDEX IF NOT EXISTS idx_videos_view_count ON videos(view_count DESC);
    END IF;
    
    -- Video view sessions indexes
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'video_view_sessions') THEN
        CREATE INDEX IF NOT EXISTS idx_view_sessions_video_id ON video_view_sessions(video_id);
        CREATE INDEX IF NOT EXISTS idx_view_sessions_user_session ON video_view_sessions(user_id, session_id);
        CREATE INDEX IF NOT EXISTS idx_view_sessions_created_at ON video_view_sessions(created_at DESC);
    END IF;
    
    -- Video upload sessions indexes
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'video_upload_sessions') THEN
        CREATE INDEX IF NOT EXISTS idx_upload_sessions_video_id ON video_upload_sessions(video_id);
        CREATE INDEX IF NOT EXISTS idx_upload_sessions_status ON video_upload_sessions(status);
    END IF;
    
    -- Video analytics indexes
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'video_analytics') THEN
        CREATE INDEX IF NOT EXISTS idx_analytics_video_id ON video_analytics(video_id);
        CREATE INDEX IF NOT EXISTS idx_analytics_date ON video_analytics(date DESC);
    END IF;
    
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- This function will be called by the application after tables are created
CREATE OR REPLACE FUNCTION setup_triggers()
RETURNS VOID AS $$
BEGIN
    -- Add triggers to tables that have updated_at columns
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'videos') THEN
        DROP TRIGGER IF EXISTS videos_updated_at_trigger ON videos;
        CREATE TRIGGER videos_updated_at_trigger 
            BEFORE UPDATE ON videos 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'video_view_sessions') THEN
        DROP TRIGGER IF EXISTS view_sessions_updated_at_trigger ON video_view_sessions;
        CREATE TRIGGER view_sessions_updated_at_trigger 
            BEFORE UPDATE ON video_view_sessions 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'video_upload_sessions') THEN
        DROP TRIGGER IF EXISTS upload_sessions_updated_at_trigger ON video_upload_sessions;
        CREATE TRIGGER upload_sessions_updated_at_trigger 
            BEFORE UPDATE ON video_upload_sessions 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
END;
$$ LANGUAGE plpgsql;

-- Grant permissions to application user (postgres in development)
GRANT USAGE ON SCHEMA public TO postgres;
GRANT CREATE ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;

-- Database ready message
SELECT 'Video Streaming Database Initialized Successfully!' AS status;
