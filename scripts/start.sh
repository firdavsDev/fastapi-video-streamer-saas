#!/bin/bash

set -e  # Exit on any error

echo "🎬 Starting Video Streaming Backend Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Check if Python is installed (for local development)
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION is installed"
    else
        print_warning "Python 3 is not installed. Required for local development."
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    directories=(
        "logs"
        "uploads" 
        "tmp"
        "ssl"
        "data/postgres"
        "data/redis"
        "data/minio"
        "data/prometheus"
        "data/grafana"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Setup environment file
setup_environment() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env file from .env.example"
            print_warning "Please review and update .env file with your specific configuration"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
}

# Install Python dependencies (for local development)
install_dependencies() {
    if [ "$1" = "local" ]; then
        print_info "Installing Python dependencies..."
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            print_status "Created virtual environment"
        fi
        
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_status "Python dependencies installed"
    fi
}

# Start services with Docker
start_docker_services() {
    print_info "Starting services with Docker Compose..."
    
    # Pull latest images
    docker-compose -f docker/docker-compose.yml pull
    
    # Build custom images
    docker-compose -f docker/docker-compose.yml build
    
    # Start services
    docker-compose -f docker/docker-compose.yml up -d
    
    print_status "Docker services started"
}

# Wait for services to be ready
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    # Wait for API to be ready
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_status "API service is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "API service failed to start after $max_attempts attempts"
            exit 1
        fi
        
        print_info "Waiting for API service... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    # Wait for MinIO to be ready
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:9000/minio/health/live >/dev/null 2>&1; then
            print_status "MinIO service is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "MinIO service failed to start after $max_attempts attempts"
            exit 1
        fi
        
        print_info "Waiting for MinIO service... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
}

# Display service URLs
display_urls() {
    print_info "🌐 Service URLs:"
    echo ""
    echo "📡 API Documentation:    http://localhost:8000/docs"
    echo "🎬 API Base URL:         http://localhost:8000/api/v1"
    echo "❤️  Health Check:        http://localhost:8000/health"
    echo ""
    echo "🗄️  MinIO Console:       http://localhost:9001 (admin/minioadmin123)"
    echo "🌸 Celery Flower:       http://localhost:5555"
    echo "📊 Prometheus:          http://localhost:9090"
    echo "📈 Grafana:             http://localhost:3000 (admin/admin123)"
    echo ""
    echo "🗃️  PostgreSQL:          localhost:5432 (postgres/postgres)"
    echo "🚀 Redis:               localhost:6379"
    echo ""
}

# Test API endpoints
test_api() {
    print_info "Testing API endpoints..."
    
    # Test health endpoint
    if response=$(curl -s http://localhost:8000/health); then
        print_status "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Test API info endpoint
    if response=$(curl -s http://localhost:8000/api/v1/info); then
        print_status "API info endpoint working"
    else
        print_error "API info endpoint failed"
        return 1
    fi
    
    print_status "Basic API tests passed"
}

# Main execution
main() {
    echo "🎬 Video Streaming Backend Setup"
    echo "=================================="
    echo ""
    
    # Parse command line arguments
    MODE="docker"
    RUN_TESTS="false"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --local)
                MODE="local"
                shift
                ;;
            --test)
                RUN_TESTS="true"
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --local    Run in local development mode"
                echo "  --test     Run API tests after startup"
                echo "  --help     Show this help message"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_docker
    check_python
    create_directories
    setup_environment
    
    if [ "$MODE" = "local" ]; then
        install_dependencies "local"
        print_info "Local development setup complete"
        print_info "To start the API locally, run:"
        echo "source venv/bin/activate"
        echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    else
        start_docker_services
        wait_for_services
        
        if [ "$RUN_TESTS" = "true" ]; then
            test_api
        fi
        
        display_urls
        
        print_status "🎉 Video Streaming Backend is ready!"
        print_info "Check the service URLs above to get started"
        print_info "Use 'docker-compose -f docker/docker-compose.yml logs -f' to view logs"
        print_info "Use 'docker-compose -f docker/docker-compose.yml down' to stop services"
    fi
}

# Run main function
main "$@"