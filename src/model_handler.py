import tensorflow as tf
import tf_keras as keras
import numpy as np
import logging
from PIL import Image
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from huggingface_hub import from_pretrained_keras
from .config import Config
from .utils import preprocess_image_vgg16

logger = logging.getLogger(__name__)

class ModelHandler:
    """Handles Keras VGG16 Cat vs Dog binary classifier model loading and inference"""

    def __init__(self):
        self.model = None
        self.classes = ['Dog', 'Cat']  # Binary classification: Dog=0, Cat=1
        self.model_loaded = False

        # Load model and classes on initialization
        self._load_model()

    def _load_model(self):
        """Load VGG16 Cat vs Dog Keras model from Hugging Face or local cache"""
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
            logger.info("VGG16 Cat vs Dog model loaded successfully from Hugging Face")

            # Print model summary for debugging
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model_loaded = False

    def predict(self, image_file) -> Dict:
        """Make prediction on uploaded cat/dog image"""
        if not self.model_loaded:
            return {'error': 'Model not loaded'}

        try:
            # Preprocess image using VGG16 preprocessing for 150x150 input
            image_array = preprocess_image_vgg16(image_file, Config.MODEL_INPUT_SIZE)

            # Add batch dimension
            image_batch = np.expand_dims(image_array, axis=0)

            # Run inference
            prediction_raw = self.model.predict(image_batch, verbose=0)

            # Get the prediction value (single value for binary classification)
            prediction_value = float(prediction_raw[0][0])

            # Binary classification logic: >= 0.5 is Cat, < 0.5 is Dog
            if prediction_value >= 0.5:
                predicted_class = 'Cat'
                confidence = prediction_value
            else:
                predicted_class = 'Dog'
                confidence = 1.0 - prediction_value

            # Create results in the expected format
            results = [
                {
                    'class': predicted_class,
                    'confidence': float(confidence),
                    'probability': f"{confidence * 100:.2f}%"
                },
                {
                    'class': 'Dog' if predicted_class == 'Cat' else 'Cat',
                    'confidence': float(1.0 - confidence),
                    'probability': f"{(1.0 - confidence) * 100:.2f}%"
                }
            ]

            return {
                'success': True,
                'predictions': results,
                'top_prediction': results[0],
                'model': 'VGG16 Cat vs Dog Classifier',
                'raw_prediction': float(prediction_value)
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
            'model_name': 'VGG16 Cat vs Dog Classifier',
            'huggingface_id': Config.HUGGINGFACE_MODEL_ID,
            'input_size': Config.MODEL_INPUT_SIZE,
            'num_classes': len(self.classes),
            'classes': self.classes,
            'total_classes': len(self.classes),
            'classification_type': 'Binary Classification'
        }

        if self.model_loaded and self.model:
            model_info.update({
                'input_shape': str(self.model.input_shape),
                'output_shape': str(self.model.output_shape)
            })

        return model_info