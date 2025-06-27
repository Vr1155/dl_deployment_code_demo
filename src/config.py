import os
from pathlib import Path

class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Model settings
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'models/cnn_model.pb'
    MODEL_INPUT_SIZE = (224, 224)  # Default input size for CNN models
    MODEL_CLASSES_FILE = os.environ.get('CLASSES_FILE') or 'models/classes.txt'

    # Image processing settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

    # Performance settings
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '1'))
    NUM_THREADS = int(os.environ.get('NUM_THREADS', '4'))

    @staticmethod
    def get_model_path():
        """Get absolute path to model file"""
        base_path = Path(__file__).parent.parent
        return base_path / Config.MODEL_PATH

    @staticmethod
    def get_classes_path():
        """Get absolute path to classes file"""
        base_path = Path(__file__).parent.parent
        return base_path / Config.MODEL_CLASSES_FILE