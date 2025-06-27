#!/bin/bash

# Docker build and run script for Cat vs Dog Classifier
# This script helps you easily build and run the Docker container

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="cat-dog-classifier"
CONTAINER_NAME="cat-dog-classifier-api"
PORT=5000

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    print_success "Docker is running"
}

# Function to check if models are downloaded
check_models() {
    if [ ! -d "models/cats_vs_dogs_classifier" ]; then
        print_warning "Model not found. Downloading the cat vs dog classifier model..."
        python download_model.py
        if [ $? -eq 0 ]; then
            print_success "Model downloaded successfully"
        else
            print_error "Failed to download model"
            exit 1
        fi
    else
        print_success "Model found"
    fi
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image: $IMAGE_NAME"

    docker build -t $IMAGE_NAME . --no-cache

    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to stop existing container
stop_container() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        print_status "Stopping existing container: $CONTAINER_NAME"
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        print_success "Container stopped and removed"
    fi
}

# Function to run container
run_container() {
    print_status "Starting Docker container: $CONTAINER_NAME on port $PORT"

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Run the container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:5000 \
        -v "$(pwd)/models:/app/models:ro" \
        -v "$(pwd)/logs:/app/logs" \
        --restart unless-stopped \
        $IMAGE_NAME

    if [ $? -eq 0 ]; then
        print_success "Container started successfully"
        print_status "API is available at: http://localhost:$PORT"
        print_status "Health check: http://localhost:$PORT/health"
        print_status "Model info: http://localhost:$PORT/model/info"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Function to show container logs
show_logs() {
    print_status "Showing container logs (press Ctrl+C to exit):"
    docker logs -f $CONTAINER_NAME
}

# Function to test the API
test_api() {
    print_status "Testing API endpoints..."

    # Wait for container to be ready
    sleep 10

    # Test health endpoint
    if curl -s "http://localhost:$PORT/health" > /dev/null; then
        print_success "Health endpoint is working"
    else
        print_error "Health endpoint is not responding"
        return 1
    fi

    # Test model info endpoint
    if curl -s "http://localhost:$PORT/model/info" > /dev/null; then
        print_success "Model info endpoint is working"
    else
        print_error "Model info endpoint is not responding"
        return 1
    fi

    print_success "API is ready!"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build       Build the Docker image"
    echo "  run         Build and run the container"
    echo "  start       Start existing container"
    echo "  stop        Stop running container"
    echo "  restart     Restart the container"
    echo "  logs        Show container logs"
    echo "  test        Test the API endpoints"
    echo "  clean       Remove container and image"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 run       # Build image and run container"
    echo "  $0 logs      # View container logs"
    echo "  $0 test      # Test API endpoints"
}

# Main logic
case "${1:-run}" in
    "build")
        check_docker
        check_models
        build_image
        ;;
    "run")
        check_docker
        check_models
        build_image
        stop_container
        run_container
        test_api
        ;;
    "start")
        check_docker
        if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
            docker start $CONTAINER_NAME
            print_success "Container started"
        else
            print_error "Container $CONTAINER_NAME not found"
        fi
        ;;
    "stop")
        stop_container
        ;;
    "restart")
        stop_container
        docker start $CONTAINER_NAME
        print_success "Container restarted"
        ;;
    "logs")
        show_logs
        ;;
    "test")
        test_api
        ;;
    "clean")
        stop_container
        if [ "$(docker images -q $IMAGE_NAME)" ]; then
            docker rmi $IMAGE_NAME
            print_success "Docker image removed"
        fi
        ;;
    "help")
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac