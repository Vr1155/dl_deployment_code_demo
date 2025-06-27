import tensorflow as tf
import numpy as np
import logging
from PIL import Image
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .config import Config
from .utils import preprocess_image

logger = logging.getLogger(__name__)

class ModelHandler:
    """Handles TensorFlow model loading and inference"""

    def __init__(self):
        self.model = None
        self.input_tensor_name = None
        self.output_tensor_name = None
        self.classes = []
        self.model_loaded = False

        # Load model and classes on initialization
        self._load_model()
        self._load_classes()

    def _load_model(self):
        """Load TensorFlow .pb model"""
        try:
            model_path = Config.get_model_path()

            if not model_path.exists():
                logger.warning(f"Model file not found at {model_path}. Model will be loaded when available.")
                return

            # Load frozen graph
            with tf.io.gfile.GFile(str(model_path), "rb") as f:
                graph_def = tf.compat.v1.GraphDef()
                graph_def.ParseFromString(f.read())

            # Import graph into TensorFlow
            with tf.Graph().as_default() as graph:
                tf.import_graph_def(graph_def, name="")

            # Create session
            self.sess = tf.compat.v1.Session(graph=graph)

            # Get input and output tensor names (you may need to adjust these based on your model)
            self.input_tensor_name = "input:0"  # Common input tensor name
            self.output_tensor_name = "output:0"  # Common output tensor name

            # Try to infer tensor names if default names don't work
            try:
                input_tensor = graph.get_tensor_by_name(self.input_tensor_name)
                output_tensor = graph.get_tensor_by_name(self.output_tensor_name)
            except KeyError:
                # If default names don't work, try to find them automatically
                ops = graph.get_operations()
                input_ops = [op for op in ops if op.type == 'Placeholder']
                output_ops = [op for op in ops if 'output' in op.name.lower() or 'prediction' in op.name.lower()]

                if input_ops:
                    self.input_tensor_name = input_ops[0].outputs[0].name
                if output_ops:
                    self.output_tensor_name = output_ops[-1].outputs[0].name

            self.model_loaded = True
            logger.info(f"Model loaded successfully from {model_path}")
            logger.info(f"Input tensor: {self.input_tensor_name}")
            logger.info(f"Output tensor: {self.output_tensor_name}")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model_loaded = False

    def _load_classes(self):
        """Load class labels from file"""
        try:
            classes_path = Config.get_classes_path()

            if not classes_path.exists():
                logger.warning(f"Classes file not found at {classes_path}. Using generic labels.")
                # Create generic class labels if file doesn't exist
                self.classes = [f"class_{i}" for i in range(10)]  # Assuming 10 classes
                return

            with open(classes_path, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]

            logger.info(f"Loaded {len(self.classes)} classes")

        except Exception as e:
            logger.error(f"Error loading classes: {str(e)}")
            self.classes = [f"class_{i}" for i in range(10)]

    def predict(self, image_file) -> Dict:
        """Make prediction on uploaded image"""
        if not self.model_loaded:
            return {'error': 'Model not loaded'}

        try:
            # Preprocess image
            image_array = preprocess_image(image_file, Config.MODEL_INPUT_SIZE)

            # Add batch dimension
            image_batch = np.expand_dims(image_array, axis=0)

            # Run inference
            predictions = self.sess.run(
                self.output_tensor_name,
                {self.input_tensor_name: image_batch}
            )

            # Process predictions
            predictions = predictions[0]  # Remove batch dimension

            # Get top 5 predictions
            top_indices = np.argsort(predictions)[-5:][::-1]

            results = []
            for idx in top_indices:
                class_name = self.classes[idx] if idx < len(self.classes) else f"class_{idx}"
                confidence = float(predictions[idx])
                results.append({
                    'class': class_name,
                    'confidence': confidence,
                    'probability': f"{confidence * 100:.2f}%"
                })

            return {
                'success': True,
                'predictions': results,
                'top_prediction': results[0] if results else None
            }

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {'error': f'Prediction failed: {str(e)}'}

    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model_loaded

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_loaded': self.model_loaded,
            'model_path': str(Config.get_model_path()),
            'input_size': Config.MODEL_INPUT_SIZE,
            'num_classes': len(self.classes),
            'classes': self.classes,
            'input_tensor': self.input_tensor_name,
            'output_tensor': self.output_tensor_name
        }