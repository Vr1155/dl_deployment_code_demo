# VGG16 Cat vs Dog Classifier

A production-ready Docker container for binary classification of cat and dog images using a fine-tuned VGG16 neural network.

## Quick Start

```bash
# Pull and run the container
docker run -d --name cat-dog-api -p 5000:5000 vr1155/cat-dog-classifier:latest

# Test the API
curl http://localhost:5000/health
```

## About

This container provides a REST API for classifying images as either cats or dogs using a VGG16-based convolutional neural network. The model achieves high accuracy on real-world cat and dog images.

## Features

- **High Accuracy**: VGG16-based binary classifier
- **Production Ready**: Ubuntu 22.04 with Python 3.10
- **REST API**: Simple HTTP endpoints for classification
- **Health Monitoring**: Built-in health checks
- **Security**: Runs as non-root user
- **Resource Optimized**: Memory limits and efficient caching

## Model Details

- **Architecture**: VGG16 (transfer learning)
- **Classes**: Cat, Dog (binary classification)
- **Input Size**: 150x150 pixels
- **Source**: Hugging Face (carlosaguayo/cats_vs_dogs)
- **Format**: TensorFlow SavedModel

## API Endpoints

### Health Check

```bash
GET /health
```

Returns API and model status.

### Model Information

```bash
GET /model/info
```

Returns detailed model information including classes and input specifications.

### Image Classification

```bash
POST /predict
```

Upload an image file for classification. Supports JPG, PNG, GIF, BMP formats.

**Example:**

```bash
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/predict
```

**Response:**

```json
{
  "success": true,
  "top_prediction": {
    "class": "Cat",
    "confidence": 0.95,
    "probability": "95.00%"
  },
  "predictions": [
    { "class": "Cat", "confidence": 0.95, "probability": "95.00%" },
    { "class": "Dog", "confidence": 0.05, "probability": "5.00%" }
  ],
  "model": "VGG16 Cat vs Dog Classifier"
}
```

## Usage Examples

### Basic Usage

```bash
# Run the container
docker run -d --name cat-dog-api -p 5000:5000 vr1155/cat-dog-classifier:latest

# Wait for startup (about 30 seconds)
sleep 30

# Test with a cat image
curl -X POST -F "image=@cat.jpg" http://localhost:5000/predict
```

### With Custom Port

```bash
docker run -d --name cat-dog-api -p 8080:5000 vr1155/cat-dog-classifier:latest
curl http://localhost:8080/health
```

### With Persistent Logs

```bash
docker run -d \
  --name cat-dog-api \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  vr1155/cat-dog-classifier:latest
```

### Production Deployment

```bash
docker run -d \
  --name cat-dog-api \
  -p 5000:5000 \
  --restart unless-stopped \
  --memory=2g \
  -v $(pwd)/logs:/app/logs \
  vr1155/cat-dog-classifier:latest
```

## Docker Compose

```yaml
version: "3.8"
services:
  cat-dog-classifier:
    image: vr1155/cat-dog-classifier:latest
    container_name: cat-dog-api
    ports:
      - "5000:5000"
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## System Requirements

### Minimum

- **RAM**: 2GB
- **CPU**: 1 core
- **Disk**: 4GB free space

### Recommended

- **RAM**: 4GB
- **CPU**: 2+ cores
- **Disk**: 8GB free space

## Environment Variables

| Variable       | Default                          | Description       |
| -------------- | -------------------------------- | ----------------- |
| `FLASK_ENV`    | `production`                     | Flask environment |
| `MODEL_PATH`   | `models/cats_vs_dogs_classifier` | Model file path   |
| `CLASSES_FILE` | `models/classes.txt`             | Class labels file |

## Health Checks

The container includes built-in health monitoring:

- **Endpoint**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 30 seconds
- **Retries**: 3

## Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- BMP

## Performance

- **Startup Time**: ~30 seconds (model loading)
- **Inference Time**: ~100-500ms per image
- **Memory Usage**: ~1.5-2GB
- **Image Size**: 3.27GB

## Security Features

- Non-root user execution
- Minimal attack surface
- Read-only model files
- Resource limits
- No sensitive data exposure

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs cat-dog-api

# Verify port availability
lsof -i :5000
```

### Out of memory errors

```bash
# Increase memory limit
docker run --memory=4g vr1155/cat-dog-classifier:latest
```

### Model loading issues

```bash
# Check model files
docker exec -it cat-dog-api ls -la /app/models/
```

## Integration Examples

### Python

```python
import requests

# Classify an image
with open('cat.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/predict', files=files)
    result = response.json()
    print(f"Prediction: {result['top_prediction']['class']}")
```

### JavaScript/Node.js

```javascript
const FormData = require("form-data");
const fs = require("fs");
const axios = require("axios");

const form = new FormData();
form.append("image", fs.createReadStream("cat.jpg"));

axios
  .post("http://localhost:5000/predict", form, {
    headers: form.getHeaders()
  })
  .then(response => {
    console.log("Prediction:", response.data.top_prediction.class);
  });
```

### cURL

```bash
# Simple classification
curl -X POST -F "image=@cat.jpg" http://localhost:5000/predict | jq '.top_prediction.class'
```

## Tags

- `latest` - Latest stable version
- `v1.0` - Version 1.0 release

## Source Code

The complete source code and documentation is available at the GitHub repository.

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues and questions, please refer to the source repository or create an issue in the project's GitHub page.
