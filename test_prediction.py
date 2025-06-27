#!/usr/bin/env python3
"""
Test script for the VGG16 Cat vs Dog Classifier API
Creates synthetic test images and sends them to the API for prediction
"""

import requests
import io
from PIL import Image, ImageDraw
import numpy as np

def create_test_image(color, size=(150, 150), pattern="solid"):
    """Create a synthetic test image"""
    image = Image.new("RGB", size, color)

    if pattern == "stripes":
        draw = ImageDraw.Draw(image)
        for i in range(0, size[1], 20):
            draw.rectangle([0, i, size[0], i+10], fill=(255, 255, 255))
    elif pattern == "spots":
        draw = ImageDraw.Draw(image)
        for i in range(0, size[0], 30):
            for j in range(0, size[1], 30):
                draw.ellipse([i, j, i+15, j+15], fill=(255, 255, 255))

    return image

def image_to_bytes(image):
    """Convert PIL Image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_api(api_url="http://localhost:5001"):
    """Test the Flask API with synthetic images"""

    print("Testing VGG16 Cat vs Dog Classifier API")
    print("=" * 50)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data['status']}")
            print(f"   Model loaded: {health_data['model_loaded']}")
        else:
            print(f"   Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   Health check error: {e}")
        return

    # Test model info endpoint
    print("\n2. Testing model info endpoint...")
    try:
        response = requests.get(f"{api_url}/model/info")
        if response.status_code == 200:
            model_info = response.json()
            print(f"   Model: {model_info.get('model_name', 'Unknown')}")
            print(f"   Classes: {model_info.get('classes', [])}")
            print(f"   Input size: {model_info.get('input_size', 'Unknown')}")
            print(f"   Total classes: {model_info.get('total_classes', 'Unknown')}")
        else:
            print(f"   Model info failed: {response.status_code}")
    except Exception as e:
        print(f"   Model info error: {e}")

    # Test prediction with different colored images
    test_cases = [
        {"color": (139, 69, 19), "name": "Brown Image (might look like dog fur)", "expected": "Dog"},
        {"color": (169, 169, 169), "name": "Gray Image (might look like cat fur)", "expected": "Cat"},
        {"color": (255, 140, 0), "name": "Orange Image (orange cats)", "expected": "Cat"},
        {"color": (255, 255, 255), "name": "White Image (neutral)", "expected": "Either"}
    ]

    print("\n3. Testing predictions with synthetic images...")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")

        # Create test image
        test_image = create_test_image(test_case['color'])
        image_bytes = image_to_bytes(test_image)

        try:
            # Send prediction request
            files = {"image": ("test_image.png", image_bytes, "image/png")}
            response = requests.post(f"{api_url}/predict", files=files)

            if response.status_code == 200:
                result = response.json()

                if result.get("success"):
                    top_pred = result["top_prediction"]
                    print(f"      Prediction: {top_pred['class']}")
                    print(f"      Confidence: {top_pred['probability']}")

                    # Show all predictions
                    print("      All predictions:")
                    for pred in result["predictions"]:
                        print(f"        {pred['class']}: {pred['probability']}")

                    # Show raw prediction value
                    if "raw_prediction" in result:
                        raw_val = result["raw_prediction"]
                        print(f"      Raw prediction value: {raw_val:.4f}")
                        print(f"      (Raw >= 0.5 = Cat, Raw < 0.5 = Dog)")
                else:
                    print(f"      Prediction failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"      API request failed: {response.status_code}")

        except Exception as e:
            print(f"      Prediction error: {e}")

    print("\n" + "=" * 50)
    print("Test completed! The API is working with synthetic images.")
    print("\nNote: These are synthetic colored images, not actual photos of cats/dogs.")
    print("For real testing, try uploading actual cat and dog photos through the web interface:")
    print("http://localhost:8501 (if using Streamlit UI)")

if __name__ == "__main__":
    test_api()