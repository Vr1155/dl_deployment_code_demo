#!/usr/bin/env python3
"""
Simple test script to demonstrate the VGG16 Fruits Classifier API
"""

import requests
import json
from PIL import Image
import io

def create_test_fruit_image():
    """Create a simple test image (red apple-like)"""
    # Create a 100x100 red image (apple-like)
    img = Image.new('RGB', (100, 100), color='red')

    # Add some variation to make it more apple-like
    for x in range(100):
        for y in range(100):
            # Create a gradient effect
            r = min(255, 200 + (x + y) // 8)
            g = max(0, 50 - (x + y) // 20)
            b = max(0, 50 - (x + y) // 20)
            img.putpixel((x, y), (r, g, b))

    return img

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5001/health")
        if response.status_code == 200:
            print("Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"Health check failed: {response.status_code}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")

def test_model_info():
    """Test the model info endpoint"""
    print("\nTesting model info endpoint...")
    try:
        response = requests.get("http://localhost:5001/model/info")
        if response.status_code == 200:
            info = response.json()
            print("Model info retrieved successfully")
            print(f"Model: {info['model_name']}")
            print(f"Classes: {info['total_classes']}")
            print(f"Input size: {info['input_size']}")
            print(f"Sample classes: {', '.join(info['classes'][:5])}...")
        else:
            print(f"Model info failed: {response.status_code}")
    except Exception as e:
        print(f"Error testing model info: {e}")

def test_prediction():
    """Test the prediction endpoint with a sample image"""
    print("\nTesting prediction endpoint...")
    try:
        # Create a test image
        test_img = create_test_fruit_image()

        # Convert to bytes
        img_buffer = io.BytesIO()
        test_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Send prediction request
        files = {'image': ('test_apple.png', img_buffer, 'image/png')}
        response = requests.post("http://localhost:5001/predict", files=files)

        if response.status_code == 200:
            result = response.json()
            print("Prediction successful")

            if result.get('success'):
                top_pred = result['top_prediction']
                print(f"Top prediction: {top_pred['class']}")
                print(f"Confidence: {top_pred['probability']}")

                print("\nTop 3 predictions:")
                for i, pred in enumerate(result['predictions'][:3], 1):
                    print(f"  {i}. {pred['class']}: {pred['probability']}")
            else:
                print(f"Prediction failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"Prediction request failed: {response.status_code}")

    except Exception as e:
        print(f"Error testing prediction: {e}")

def main():
    """Main test function"""
    print("VGG16 Fruits Classifier API Test")
    print("=" * 50)

    # Test all endpoints
    test_health_endpoint()
    test_model_info()
    test_prediction()

    print("\nAPI testing completed!")
    print("\nTips:")
    print("- Try uploading real fruit images for better predictions")
    print("- The model works best with 100x100 fruit images")
    print("- Supported formats: PNG, JPG, JPEG, GIF, BMP")

if __name__ == "__main__":
    main()