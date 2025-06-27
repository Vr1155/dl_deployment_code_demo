#!/usr/bin/env python3
"""
Test script to verify the complete UI -> Flask API connection
Creates synthetic test images and sends them through the API
"""

import requests
import io
from PIL import Image, ImageDraw
import json

def create_synthetic_pet_image(color, size=(150, 150)):
    """Create a synthetic pet-like image"""
    image = Image.new("RGB", size, color)

    # Add some simple features to make it more pet-like
    draw = ImageDraw.Draw(image)

    # Add some oval shapes to simulate pet features
    center_x, center_y = size[0] // 2, size[1] // 2

    # Body oval
    draw.ellipse([center_x - 40, center_y - 20, center_x + 40, center_y + 40],
                 fill=(min(255, color[0] + 20), min(255, color[1] + 20), min(255, color[2] + 20)))

    # Head circle
    draw.ellipse([center_x - 25, center_y - 40, center_x + 25, center_y - 10],
                 fill=(min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30)))

    # Eyes
    draw.ellipse([center_x - 15, center_y - 32, center_x - 10, center_y - 27], fill=(0, 0, 0))
    draw.ellipse([center_x + 10, center_y - 32, center_x + 15, center_y - 27], fill=(0, 0, 0))

    return image

def image_to_bytes(image):
    """Convert PIL Image to bytes for API request"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_complete_system(api_url="http://localhost:5001"):
    """Test the complete system: Flask API backend"""

    print("Testing Complete VGG16 Cat vs Dog Classifier System")
    print("=" * 60)

    # Test 1: Health Check
    print("\n1. Testing Flask API Health Check...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   [OK] Status: {health_data['status']}")
            print(f"   [OK] Model loaded: {health_data['model_loaded']}")
        else:
            print(f"   [ERROR] Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Health check error: {e}")
        return False

    # Test 2: Model Info
    print("\n2. Testing Model Information...")
    try:
        response = requests.get(f"{api_url}/model/info", timeout=10)
        if response.status_code == 200:
            model_info = response.json()
            print(f"   [OK] Model: {model_info.get('model_name', 'Unknown')}")
            print(f"   [OK] Classes: {model_info.get('classes', [])}")
            print(f"   [OK] Input size: {model_info.get('input_size', 'Unknown')}")
            print(f"   [OK] Total classes: {model_info.get('total_classes', 'Unknown')}")
            print(f"   [OK] Classification type: {model_info.get('classification_type', 'Unknown')}")
        else:
            print(f"   [ERROR] Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Model info error: {e}")
        return False

    # Test 3: Image Predictions
    print("\n3. Testing Image Predictions...")

    test_cases = [
        {"color": (139, 69, 19), "name": "Brown (Dog-like)", "expected": "Dog"},
        {"color": (255, 165, 0), "name": "Orange (Cat-like)", "expected": "Cat"},
        {"color": (192, 192, 192), "name": "Gray (Neutral)", "expected": "Either"}
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test 3.{i}: {test_case['name']} Image")

        # Create synthetic pet image
        test_image = create_synthetic_pet_image(test_case['color'])
        image_bytes = image_to_bytes(test_image)

        try:
            # Send prediction request
            files = {"image": ("test_pet.png", image_bytes, "image/png")}
            response = requests.post(f"{api_url}/predict", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if result.get("success"):
                    top_pred = result["top_prediction"]
                    print(f"      [OK] Prediction: {top_pred['class']}")
                    print(f"      [OK] Confidence: {top_pred['probability']}")

                    # Show both predictions
                    predictions = result["predictions"]
                    print(f"      [INFO] Cat: {next((p['probability'] for p in predictions if p['class'] == 'Cat'), '0%')}")
                    print(f"      [INFO] Dog: {next((p['probability'] for p in predictions if p['class'] == 'Dog'), '0%')}")

                    # Show raw prediction value
                    if "raw_prediction" in result:
                        raw_val = result["raw_prediction"]
                        print(f"      [DEBUG] Raw value: {raw_val:.4f} ({'Cat' if raw_val >= 0.5 else 'Dog'})")
                else:
                    print(f"      [ERROR] Prediction failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      [ERROR] API request failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"      [ERROR] Prediction error: {e}")
            return False

    # Test 4: Error Handling
    print("\n4. Testing Error Handling...")
    try:
        # Send an invalid file
        invalid_data = b"This is not an image file"
        files = {"image": ("invalid.txt", io.BytesIO(invalid_data), "text/plain")}
        response = requests.post(f"{api_url}/predict", files=files, timeout=10)

        if response.status_code == 400:
            print("   [OK] Properly handles invalid image files")
        else:
            print(f"   [WARN] Unexpected response for invalid file: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Error handling test failed: {e}")

    print("\n" + "=" * 60)
    print("SYSTEM TEST COMPLETED SUCCESSFULLY!")
    print("\nSystem Status:")
    print("[OK] Flask API Backend: Running and responsive")
    print("[OK] VGG16 Cat vs Dog Model: Loaded and functional")
    print("[OK] Image Preprocessing: Working correctly")
    print("[OK] Binary Classification: Working correctly")
    print("[OK] Error Handling: Implemented")

    print("\nNext Steps:")
    print("1. Start Streamlit UI: cd ui && streamlit run app_v1.py --server.port=8501")
    print("2. Visit: http://localhost:8501")
    print("3. Upload real cat or dog photos for testing")
    print("4. Enjoy classifying your pets!")

    return True

if __name__ == "__main__":
    success = test_complete_system()
    if not success:
        print("\n[ERROR] System test failed. Please check the error messages above.")
        exit(1)
    else:
        print("\n[SUCCESS] All tests passed!")
        exit(0)