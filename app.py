from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from src.model_handler import ModelHandler
from src.config import Config
from src.utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend communication
    CORS(app)

    # Initialize model handler
    model_handler = ModelHandler()

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'model_loaded': model_handler.is_model_loaded()
        })

    @app.route('/predict', methods=['POST'])
    def predict():
        """Main prediction endpoint"""
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400

            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400

            # Get prediction from model
            prediction_result = model_handler.predict(image_file)

            return jsonify(prediction_result)

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/model/info', methods=['GET'])
    def model_info():
        """Get model information"""
        return jsonify(model_handler.get_model_info())

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)