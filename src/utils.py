import numpy as np
import logging
import os
from PIL import Image
from pathlib import Path
from typing import Tuple
import io

def setup_logging():
    """Setup application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

def preprocess_image_vgg16(image_file, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Preprocess uploaded image for VGG16 model inference

    Args:
        image_file: Uploaded image file
        target_size: Target size (width, height) for resizing

    Returns:
        Preprocessed image as numpy array suitable for VGG16
    """
    from tensorflow.keras.applications.vgg16 import preprocess_input

    # Read image
    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize image to target size
    image = image.resize(target_size, Image.Resampling.LANCZOS)

    # Convert to numpy array
    image_array = np.array(image, dtype=np.float32)

    # Apply VGG16 preprocessing (this handles normalization)
    image_array = preprocess_input(image_array)

    return image_array

def preprocess_image(image_file, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Generic preprocess uploaded image for model inference (keeping for backward compatibility)

    Args:
        image_file: Uploaded image file
        target_size: Target size (width, height) for resizing

    Returns:
        Preprocessed image as numpy array
    """
    # Read image
    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize image
    image = image.resize(target_size, Image.Resampling.LANCZOS)

    # Convert to numpy array
    image_array = np.array(image, dtype=np.float32)

    # Normalize pixel values to [0, 1]
    image_array = image_array / 255.0

    return image_array

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['logs', 'models', 'uploads', 'temp']

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def validate_image_file(image_file) -> Tuple[bool, str]:
    """
    Validate uploaded image file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not image_file:
        return False, "No file provided"

    if image_file.filename == '':
        return False, "No file selected"

    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    if not allowed_file(image_file.filename, allowed_extensions):
        return False, f"File type not allowed. Supported types: {', '.join(allowed_extensions)}"

    # Try to open image to validate it's a valid image file
    try:
        image_file.seek(0)  # Reset file pointer
        image = Image.open(image_file)
        image.verify()  # Verify it's a valid image
        image_file.seek(0)  # Reset file pointer again for actual processing
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"