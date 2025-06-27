#!/bin/bash

# Multi-platform Docker build script for Cat vs Dog Classifier
# Builds for both ARM64 and x86/AMD64 architectures

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="vr1155"
IMAGE_NAME="cat-dog-classifier"
VERSION="v1.0"

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

# Function to check if logged into Docker Hub
check_docker_login() {
    if ! docker info | grep -q "Username:"; then
        print_warning "Not logged into Docker Hub. Please run 'docker login' first."
        read -p "Do you want to login now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker login
        else
            print_error "Docker Hub login required for pushing images."
            exit 1
        fi
    fi
    print_success "Docker Hub login verified"
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

# Function to setup buildx for multi-platform builds
setup_buildx() {
    print_status "Setting up Docker buildx for multi-platform builds..."

    # Create builder if it doesn't exist
    if ! docker buildx ls | grep -q "multiplatform-builder"; then
        docker buildx create --name multiplatform-builder --use
        print_success "Created multiplatform-builder"
    else
        docker buildx use multiplatform-builder
        print_success "Using existing multiplatform-builder"
    fi

    # Bootstrap the builder
    docker buildx inspect --bootstrap
    print_success "Buildx setup complete"
}

# Function to build for specific platform
build_single_platform() {
    local platform=$1
    local tag_suffix=$2

    print_status "Building for platform: $platform"

    docker buildx build \
        --platform $platform \
        -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION-$tag_suffix \
        -t $DOCKER_USERNAME/$IMAGE_NAME:latest-$tag_suffix \
        --push .

    print_success "Built and pushed for $platform"
}

# Function to build multi-platform image
build_multiplatform() {
    print_status "Building multi-platform image..."

    # Build and push multi-platform image
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION \
        -t $DOCKER_USERNAME/$IMAGE_NAME:latest \
        --push .

    print_success "Multi-platform build complete"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  amd64       Build for x86/AMD64 only"
    echo "  arm64       Build for ARM64 only"
    echo "  multi       Build for both architectures (default)"
    echo "  setup       Setup buildx only"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 amd64    # Build for x86/AMD64 systems"
    echo "  $0 multi    # Build for both ARM64 and x86/AMD64"
}

# Function to display build information
show_build_info() {
    echo ""
    print_status "Build Information:"
    echo "  Docker Username: $DOCKER_USERNAME"
    echo "  Image Name: $IMAGE_NAME"
    echo "  Version: $VERSION"
    echo "  Available Tags:"
    echo "    - $DOCKER_USERNAME/$IMAGE_NAME:latest (multi-platform)"
    echo "    - $DOCKER_USERNAME/$IMAGE_NAME:$VERSION (multi-platform)"
    echo "    - $DOCKER_USERNAME/$IMAGE_NAME:latest-amd64 (x86/AMD64)"
    echo "    - $DOCKER_USERNAME/$IMAGE_NAME:latest-arm64 (ARM64)"
    echo ""
}

# Main logic
case "${1:-multi}" in
    "amd64")
        print_status "Building for x86/AMD64 architecture only"
        check_docker
        check_docker_login
        check_models
        setup_buildx
        build_single_platform "linux/amd64" "amd64"
        show_build_info
        ;;
    "arm64")
        print_status "Building for ARM64 architecture only"
        check_docker
        check_docker_login
        check_models
        setup_buildx
        build_single_platform "linux/arm64" "arm64"
        show_build_info
        ;;
    "multi")
        print_status "Building multi-platform image (ARM64 + x86/AMD64)"
        check_docker
        check_docker_login
        check_models
        setup_buildx
        build_multiplatform
        show_build_info
        ;;
    "setup")
        print_status "Setting up buildx only"
        check_docker
        setup_buildx
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

print_success "Build process completed!"
echo ""
print_status "Usage instructions:"
echo "For x86/AMD64 systems:"
echo "  docker run -d --name cat-dog-api -p 5000:5000 $DOCKER_USERNAME/$IMAGE_NAME:latest-amd64"
echo ""
echo "For ARM64 systems:"
echo "  docker run -d --name cat-dog-api -p 5000:5000 $DOCKER_USERNAME/$IMAGE_NAME:latest-arm64"
echo ""
echo "For automatic platform detection:"
echo "  docker run -d --name cat-dog-api -p 5000:5000 $DOCKER_USERNAME/$IMAGE_NAME:latest"