FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV MODEL_PATH=models/cats_vs_dogs_classifier
ENV CLASSES_FILE=models/classes.txt

WORKDIR /app

RUN apt-get update && apt-get install -y \
    # Python and pip
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3.10-venv \
    # Build tools and compilers
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # System libraries for OpenCV and image processing
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    # For TensorFlow
    libhdf5-dev \
    pkg-config \
    # Networking tools
    curl \
    wget \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create symbolic links for python
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

RUN pip install --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p logs models uploads temp && \
    chmod 755 logs models uploads temp

COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --user-group appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

USER appuser

# Expose port 5000 (Flask default)
EXPOSE 5000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=10)" || exit 1

# Run the Flask application
CMD ["python", "app.py"]