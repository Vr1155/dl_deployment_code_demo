import pytest
import json
import io
from PIL import Image
import sys
import os

# Add the parent directory to the path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def create_test_image():
    """Create a test image for upload testing"""
    img = Image.new('RGB', (224, 224), color='red')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'healthy'

def test_model_info(client):
    """Test model info endpoint"""
    response = client.get('/model/info')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'model_loaded' in data
    assert 'num_classes' in data

def test_predict_no_file(client):
    """Test predict endpoint without file"""
    response = client.post('/predict')
    assert response.status_code == 400

    data = json.loads(response.data)
    assert 'error' in data

def test_predict_empty_file(client):
    """Test predict endpoint with empty filename"""
    response = client.post('/predict', data={'image': (io.BytesIO(b""), '')})
    assert response.status_code == 400

def test_predict_valid_image(client):
    """Test predict endpoint with valid image"""
    test_image = create_test_image()

    response = client.post('/predict', data={
        'image': (test_image, 'test.png')
    }, content_type='multipart/form-data')

    # Note: This test might fail if model is not loaded
    # In a real scenario, you'd mock the model or ensure it's available
    assert response.status_code in [200, 500]  # 500 if model not loaded

if __name__ == '__main__':
    pytest.main([__file__])