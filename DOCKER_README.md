# Docker Deployment Guide - Cat vs Dog Classifier

This guide will help you deploy the VGG16 Cat vs Dog Classifier using Docker containers in an Ubuntu Linux environment.

## Prerequisites

- Docker installed and running on your system
- At least 4GB of available RAM
- Internet connection for downloading the model

## Quick Start

### Option 1: Using the Convenience Script (Recommended)

```bash
# Make the script executable (if not already)
chmod +x docker-run.sh

# Build and run the container
./docker-run.sh run

# Check logs
./docker-run.sh logs

# Stop the container
./docker-run.sh stop
```

### Option 2: Using Docker Compose

```bash
# Build and start the services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop the services
docker-compose down
```

### Option 3: Manual Docker Commands

```bash
# Build the image
docker build -t cat-dog-classifier .

# Run the container
docker run -d \
  --name cat-dog-classifier-api \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/logs:/app/logs \
  cat-dog-classifier
```

## Docker Script Commands

The `docker-run.sh` script provides several convenient commands:

- `./docker-run.sh run` - Build image and run container (default)
- `./docker-run.sh build` - Build the Docker image only
- `./docker-run.sh start` - Start existing container
- `./docker-run.sh stop` - Stop running container
- `./docker-run.sh restart` - Restart the container
- `./docker-run.sh logs` - Show container logs
- `./docker-run.sh test` - Test API endpoints
- `./docker-run.sh clean` - Remove container and image
- `./docker-run.sh help` - Show help message

## Docker Image Details

### Base Image

- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.10
- **Architecture**: Multi-platform support

### Installed Packages

- Python 3.10 with pip
- TensorFlow 2.13.0
- Flask web framework
- OpenCV for image processing
- All required ML dependencies

### Security Features

- Non-root user execution
- Minimal attack surface
- Read-only model volume mounts
- Resource limits configured

## API Endpoints

Once the container is running, the following endpoints are available:

- `http://localhost:5000/health` - Health check
- `http://localhost:5000/model/info` - Model information
- `http://localhost:5000/predict` - Image classification (POST)

## Testing the Deployment

### 1. Health Check

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{ "model_loaded": true, "status": "healthy" }
```

### 2. Model Information

```bash
curl http://localhost:5000/model/info
```

### 3. Image Classification

```bash
# Using a test image
curl -X POST -F "image=@your_cat_or_dog_image.jpg" http://localhost:5000/predict
```

## Volume Mounts

The container uses the following volume mounts:

- `./models:/app/models:ro` - Model files (read-only)
- `./logs:/app/logs` - Application logs (read-write)

## Environment Variables

The following environment variables are configured:

- `FLASK_ENV=production`
- `MODEL_PATH=models/cats_vs_dogs_classifier`
- `CLASSES_FILE=models/classes.txt`
- `PYTHONPATH=/app`

## Resource Requirements

### Minimum Requirements

- **RAM**: 2GB
- **CPU**: 1 core
- **Disk**: 2GB free space

### Recommended Requirements

- **RAM**: 4GB
- **CPU**: 2 cores
- **Disk**: 5GB free space

## Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   # Change the port in docker-run.sh or use:
   docker run -p 5001:5000 cat-dog-classifier
   ```

2. **Model Not Found**

   ```bash
   # Download the model first
   python download_model.py
   ```

3. **Permission Denied**

   ```bash
   # Make script executable
   chmod +x docker-run.sh
   ```

4. **Docker Not Running**
   ```bash
   # Start Docker service
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop on macOS/Windows
   ```

### Viewing Logs

```bash
# Using the script
./docker-run.sh logs

# Using Docker directly
docker logs -f cat-dog-classifier-api

# Check container status
docker ps -a
```

### Debugging Container Issues

```bash
# Enter the container for debugging
docker exec -it cat-dog-classifier-api /bin/bash

# Check container resource usage
docker stats cat-dog-classifier-api
```

## Performance Optimization

### 1. Memory Limits

The container is configured with memory limits:

- Limit: 2GB
- Reservation: 1GB

### 2. CPU Optimization

- The container uses all available CPU cores for inference
- TensorFlow is optimized for CPU usage

### 3. Model Caching

- Models are cached locally after first download
- Subsequent runs use cached models for faster startup

## Production Deployment

### Using Docker Compose for Production

```yaml
version: "3.8"
services:
  flask-cnn-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Health Checks

The container includes built-in health checks:

- Interval: 30 seconds
- Timeout: 30 seconds
- Retries: 3
- Start period: 60 seconds

## Security Considerations

1. **Non-root User**: Container runs as non-root user `appuser`
2. **Read-only Volumes**: Model files are mounted read-only
3. **Minimal Base Image**: Uses Ubuntu with only necessary packages
4. **Resource Limits**: Prevents resource exhaustion

## Monitoring

### Container Metrics

```bash
# View resource usage
docker stats cat-dog-classifier-api

# View logs with timestamps
docker logs -t cat-dog-classifier-api
```

### Application Logs

Logs are written to the `./logs` directory and include:

- Application startup/shutdown
- API requests and responses
- Model loading status
- Error messages

## Updating the Application

```bash
# Stop current container
./docker-run.sh stop

# Pull latest changes
git pull

# Rebuild and restart
./docker-run.sh run
```

## Scaling

For high-traffic scenarios, consider:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Containers**: Scale with Docker Swarm or Kubernetes
3. **Caching**: Implement Redis for response caching
4. **GPU Support**: Modify Dockerfile for GPU acceleration

## Support

If you encounter issues:

1. Check the logs: `./docker-run.sh logs`
2. Verify Docker is running: `docker --version`
3. Test endpoints: `./docker-run.sh test`
4. Review this documentation

For more help, create an issue in the project repository.
