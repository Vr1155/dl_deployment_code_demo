# VGG16 Cat vs Dog Classifier Flask API

A production-ready Flask API for deploying the VGG16 Cat vs Dog Classifier model using TensorFlow/Keras. This application performs binary classification to distinguish between cats and dogs in uploaded images. The app is designed to run in Docker containers and provides RESTful endpoints for pet image classification.

## Features

- **VGG16 Cat vs Dog Model**: Pre-trained binary classifier for cat and dog detection
- **Hugging Face Integration**: Automatic model download from Hugging Face Hub
- **Docker Ready**: Containerized application for easy deployment
- **REST API**: Simple HTTP endpoints for pet image predictions
- **Image Processing**: VGG16-optimized preprocessing and validation (150x150 input)
- **Health Monitoring**: Health check endpoints for monitoring
- **Logging**: Comprehensive logging system
- **CORS Support**: Ready for Streamlit frontend integration
- **Production Ready**: Optimized for production deployment

## Project Structure

```
app.py                 # Main Flask application
src/
    __init__.py
    config.py         # Application configuration
    model_handler.py  # Model loading and inference
    utils.py          # Utility functions
models/
    .gitkeep
    classes.txt       # Cat and Dog class labels
    cats_vs_dogs_classifier/  # Downloaded Keras model
tests/
    __init__.py
    test_app.py       # Unit tests
logs/
    .gitkeep
Dockerfile            # Docker configuration
docker-compose.yml    # Docker Compose setup
requirements.txt      # Python dependencies
.dockerignore        # Docker ignore file
README.md            # This file
```

## Quick Start

### 1. Download the VGG16 Cat vs Dog Model

The model will be automatically downloaded from Hugging Face on first run, or you can pre-download it:

```bash
# Install dependencies
pip install tensorflow tf-keras huggingface_hub pillow flask flask-cors

# Download model and generate cat/dog class labels
python download_model.py
```

### 2. Using Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t cnn-flask-api .
docker run -p 5000:5000 cnn-flask-api
```

### 3. Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download the model (if not already done)
python download_model.py

# Run the application
python app.py

# On macOS, if port 5000 is occupied by AirPlay:
PORT=5001 python app.py
```

## API Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Model Information

```http
GET /model/info
```

**Response:**

```json
{
  "model_loaded": true,
  "model_name": "VGG16 Cat vs Dog Classifier",
  "huggingface_id": "carlosaguayo/cats_vs_dogs",
  "input_size": [150, 150],
  "num_classes": 2,
  "total_classes": 2,
  "classes": ["Dog", "Cat"],
  "input_shape": "(None, 150, 150, 3)",
  "output_shape": "(None, 1)"
}
```

### Image Prediction

```http
POST /predict
Content-Type: multipart/form-data
```

**Parameters:**

- `image`: Image file (PNG, JPG, JPEG, GIF, BMP)

**Response:**

```json
{
  "success": true,
  "model": "VGG16 Cat vs Dog Classifier",
  "predictions": [
    {
      "class": "Dog"
    },
    {
      "class": "Cat"
    }
  ],
  "top_prediction": {
    "class": "Cat"
  }
}
```

## Testing the API

A test script is provided to demonstrate all endpoints:

```bash
# Test all API endpoints with synthetic cat and dog images
python test_prediction.py
```

This will test:

- Health check endpoint
- Model info endpoint
- Prediction endpoint with sample cat and dog images

## Configuration

Key configuration options in `src/config.py`:

- `MODEL_PATH`: Path to the Keras model directory
- `MODEL_INPUT_SIZE`: Input image size (150, 150 for VGG16)
- `MODEL_CLASSES_FILE`: Path to classes.txt file
- `HUGGINGFACE_MODEL_ID`: Hugging Face model identifier
- `MAX_CONTENT_LENGTH`: Maximum upload file size
- `ALLOWED_EXTENSIONS`: Allowed image file extensions

## Environment Variables

You can override configuration using environment variables:

- `MODEL_PATH`: Path to model file
- `CLASSES_FILE`: Path to classes file
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Environment (development, production)

## Model Requirements

Your TensorFlow model should:

1. Be saved as a `.pb` (frozen graph) file
2. Have predictable input/output tensor names
3. Accept image input of shape `[batch, height, width, channels]`
4. Output class probabilities/logits

### Default Tensor Names

- Input: `input:0`
- Output: `output:0`

If your model uses different tensor names, the application will try to auto-detect them.

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Production Deployment

### Docker Deployment

1. Build the image:

```bash
docker build -t cnn-flask-api .
```

2. Run with environment variables:

```bash
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/models:/app/models:ro \
  --name cnn-api \
  cnn-flask-api
```

### Using Gunicorn (Production WSGI Server)

```bash
# Install gunicorn (included in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## Monitoring

The application provides health check endpoints for monitoring:

- `/health`: Basic health status
- Logs are written to `logs/app.log`
- Docker health checks are configured in `docker-compose.yml`

## Integration with Streamlit Frontend

This Flask API is designed to work with a separate Streamlit frontend. The CORS configuration allows cross-origin requests from your Streamlit app.

Example Streamlit integration:

```python
import streamlit as st
import requests

# Upload cat or dog image in Streamlit
uploaded_file = st.file_uploader("Choose a cat or dog image...")

if uploaded_file is not None:
    # Send to Flask API
    files = {"image": uploaded_file}
    response = requests.post("http://localhost:5000/predict", files=files)

    if response.status_code == 200:
        prediction = response.json()
        top_pred = prediction['top_prediction']
        emoji = "🐱" if top_pred['class'] == 'Cat' else "🐶"
        st.success(f"{emoji} Prediction: {top_pred['class']}")
        st.info(f"Model: {prediction['model']}")
```

## Troubleshooting

### Common Issues

1. **Model not loading**: Check that your `.pb` file is in the correct location and the path in `config.py` is correct.

2. **Tensor name errors**: Update the tensor names in `model_handler.py` to match your model's input/output tensors.

3. **Image preprocessing errors**: Ensure your model expects the correct input format (RGB, normalized, etc.).

4. **Memory issues**: Adjust the number of workers or batch size based on your available memory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
