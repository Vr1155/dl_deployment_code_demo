#!/usr/bin/env python3
"""
Script to download the VGG16 Cat vs Dog Classifier model and generate class labels
"""

import os
import sys
from pathlib import Path
from huggingface_hub import from_pretrained_keras
import tf_keras as keras

def get_class_labels():
    """
    Generate the 2 class names for the Cat vs Dog binary classifier
    """
    class_labels = ['Dog', 'Cat']  # Binary classification: Dog=0, Cat=1
    return class_labels

def download_model():
    """Download the VGG16 Cat vs Dog Classifier model from Hugging Face"""

    print("Downloading VGG16 Cat vs Dog Classifier model from Hugging Face...")

    try:
        # Download model
        model = from_pretrained_keras("carlosaguayo/cats_vs_dogs")

        # Create models directory
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)

        # Save model locally
        model_path = models_dir / "cats_vs_dogs_classifier"
        model.save(str(model_path))

        print(f"Model downloaded and saved to: {model_path}")
        print(f"Model input shape: {model.input_shape}")
        print(f"Model output shape: {model.output_shape}")

        # Generate and save class labels
        class_labels = get_class_labels()
        classes_file = models_dir / "classes.txt"

        with open(classes_file, 'w') as f:
            for class_label in class_labels:
                f.write(f"{class_label}\n")

        print(f"Generated {len(class_labels)} class labels and saved to: {classes_file}")

        return True

    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        return False

def main():
    """Main function"""
    print("VGG16 Cat vs Dog Classifier Model Downloader")
    print("=" * 50)

    if download_model():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Run the Flask app: python app.py")
        print("2. Or use Docker: docker-compose up --build")
        print("3. Test the API at: http://localhost:5000/health")
        print("4. Upload cat or dog images to classify!")
    else:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()