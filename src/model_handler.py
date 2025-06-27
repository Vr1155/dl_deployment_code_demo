import tensorflow as tf
import tf_keras as keras
import numpy as np
import logging
from PIL import Image
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from huggingface_hub import from_pretrained_keras
from tensorflow.keras.applications.vgg16 import preprocess_input
from .config import Config
from .utils import preprocess_image_vgg16

logger = logging.getLogger(__name__)

class ModelHandler:
    """Handles Keras VGG16 Fruits model loading and inference"""

    def __init__(self):
        self.model = None
        self.classes = []
        self.model_loaded = False

        # Load model and classes on initialization
        self._load_model()
        self._load_classes()

    def _load_model(self):
        """Load VGG16 Fruits Keras model from Hugging Face or local cache"""
        try:
            model_path = Config.get_model_path()

            # Try to load from local cache first
            if model_path.exists():
                try:
                    logger.info(f"Loading model from local cache: {model_path}")
                    self.model = keras.models.load_model(str(model_path))
                    self.model_loaded = True
                    logger.info("Model loaded successfully from local cache")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load from local cache: {str(e)}")

            # Download from Hugging Face if not available locally
            logger.info(f"Downloading model from Hugging Face: {Config.HUGGINGFACE_MODEL_ID}")
            self.model = from_pretrained_keras(Config.HUGGINGFACE_MODEL_ID)

            # Save model locally for future use
            model_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(model_path))
            logger.info(f"Model saved to local cache: {model_path}")

            self.model_loaded = True
            logger.info("VGG16 Fruits model loaded successfully from Hugging Face")

            # Print model summary for debugging
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model_loaded = False

    def _load_classes(self):
        """Load fruit class labels from file"""
        try:
            classes_path = Config.get_classes_path()

            if not classes_path.exists():
                logger.warning(f"Classes file not found at {classes_path}. Using generic labels.")
                # Create generic class labels for 131 fruit classes
                self.classes = [f"fruit_{i}" for i in range(131)]
                return

            with open(classes_path, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]

            logger.info(f"Loaded {len(self.classes)} fruit classes")

        except Exception as e:
            logger.error(f"Error loading classes: {str(e)}")
            # Default to 131 generic fruit classes as per model card
            self.classes = [f"fruit_{i}" for i in range(131)]

    def predict(self, image_file) -> Dict:
        """Make prediction on uploaded fruit image"""
        if not self.model_loaded:
            return {'error': 'Model not loaded'}

        try:
            # Preprocess image using VGG16 preprocessing
            image_array = preprocess_image_vgg16(image_file, Config.MODEL_INPUT_SIZE)

            # Add batch dimension
            image_batch = np.expand_dims(image_array, axis=0)

            # Run inference
            predictions = self.model.predict(image_batch, verbose=0)

            # Process predictions - get probabilities
            predictions = predictions[0]  # Remove batch dimension

            # Get top 5 predictions
            top_indices = np.argsort(predictions)[-5:][::-1]

            results = []
            for idx in top_indices:
                class_name = self.classes[idx] if idx < len(self.classes) else f"fruit_{idx}"
                confidence = float(predictions[idx])
                results.append({
                    'class': class_name,
                    'confidence': confidence,
                    'probability': f"{confidence * 100:.2f}%"
                })

            return {
                'success': True,
                'predictions': results,
                'top_prediction': results[0] if results else None,
                'model': 'VGG16 Fruits Classifier'
            }

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {'error': f'Prediction failed: {str(e)}'}

    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model_loaded

    def get_model_info(self) -> Dict:
        """Get model information"""
        model_info = {
            'model_loaded': self.model_loaded,
            'model_path': str(Config.get_model_path()),
            'model_name': 'VGG16 Fruits Classifier',
            'huggingface_id': Config.HUGGINGFACE_MODEL_ID,
            'input_size': Config.MODEL_INPUT_SIZE,
            'num_classes': len(self.classes),
            'classes': self.classes[:10] if len(self.classes) > 10 else self.classes,  # Show first 10 classes
            'total_classes': len(self.classes)
        }

        if self.model_loaded and self.model:
            model_info.update({
                'input_shape': str(self.model.input_shape),
                'output_shape': str(self.model.output_shape)
            })

        return model_info