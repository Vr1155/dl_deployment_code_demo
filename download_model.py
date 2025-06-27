#!/usr/bin/env python3
"""
Script to download the VGG16 Fruits Classifier model and generate class labels
"""

import os
import sys
from pathlib import Path
from huggingface_hub import from_pretrained_keras
import tf_keras as keras

def get_fruit_classes():
    """
    Generate the 131 fruit class names based on the Fruits-360 dataset
    These are the actual fruit categories from the dataset
    """
    fruit_classes = [
        'Apple Braeburn', 'Apple Crimson Snow', 'Apple Golden 1', 'Apple Golden 2', 'Apple Golden 3',
        'Apple Granny Smith', 'Apple Pink Lady', 'Apple Red 1', 'Apple Red 2', 'Apple Red 3',
        'Apple Red Delicious', 'Apple Red Yellow 1', 'Apple Red Yellow 2', 'Apricot', 'Avocado',
        'Avocado ripe', 'Banana', 'Banana Lady Finger', 'Banana Red', 'Beetroot', 'Blueberry',
        'Cactus fruit', 'Cantaloupe 1', 'Cantaloupe 2', 'Carambula', 'Cauliflower', 'Cherry 1',
        'Cherry 2', 'Cherry Rainier', 'Cherry Wax Black', 'Cherry Wax Red', 'Cherry Wax Yellow',
        'Chestnut', 'Clementine', 'Cocos', 'Corn', 'Corn Husk', 'Cucumber Ripe', 'Cucumber Ripe 2',
        'Dates', 'Eggplant', 'Fig', 'Ginger Root', 'Granadilla', 'Grape Blue', 'Grape Pink',
        'Grape White', 'Grape White 2', 'Grape White 3', 'Grape White 4', 'Grapefruit Pink',
        'Grapefruit White', 'Guava', 'Hazelnut', 'Huckleberry', 'Kaki', 'Kiwi', 'Kohlrabi',
        'Kumquats', 'Lemon', 'Lemon Meyer', 'Limes', 'Lychee', 'Mandarine', 'Mango', 'Mango Red',
        'Mangostan', 'Maracuja', 'Melon Piel de Sapo', 'Mulberry', 'Nectarine', 'Nectarine Flat',
        'Nut Forest', 'Nut Pecan', 'Onion Red', 'Onion Red Peeled', 'Onion White', 'Orange',
        'Papaya', 'Passion Fruit', 'Peach', 'Peach 2', 'Peach Flat', 'Pear', 'Pear 2',
        'Pear Abate', 'Pear Forelle', 'Pear Kaiser', 'Pear Monster', 'Pear Red', 'Pear Stone',
        'Pear Williams', 'Pepino', 'Pepper Green', 'Pepper Orange', 'Pepper Red', 'Pepper Yellow',
        'Physalis', 'Physalis with Husk', 'Pineapple', 'Pineapple Mini', 'Pitahaya Red', 'Plum',
        'Plum 2', 'Plum 3', 'Pomegranate', 'Pomelo Sweetie', 'Potato Red', 'Potato Red Washed',
        'Potato Sweet', 'Potato White', 'Quince', 'Rambutan', 'Raspberry', 'Redcurrant', 'Salak',
        'Strawberry', 'Strawberry Wedge', 'Tamarillo', 'Tangelo', 'Tomato 1', 'Tomato 2',
        'Tomato 3', 'Tomato 4', 'Tomato Cherry Red', 'Tomato Heart', 'Tomato Maroon', 'Tomato Yellow',
        'Tomato not Ripened', 'Walnut', 'Watermelon'
    ]
    return fruit_classes

def download_model():
    """Download the VGG16 Fruits Classifier model from Hugging Face"""

    print("Downloading VGG16 Fruits Classifier model from Hugging Face...")

    try:
        # Download model
        model = from_pretrained_keras("Adriana213/vgg16-fruit-classifier")

        # Create models directory
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)

        # Save model locally
        model_path = models_dir / "vgg16-fruit-classifier"
        model.save(str(model_path))

        print(f"Model downloaded and saved to: {model_path}")
        print(f"Model input shape: {model.input_shape}")
        print(f"Model output shape: {model.output_shape}")

        # Generate and save class labels
        fruit_classes = get_fruit_classes()
        classes_file = models_dir / "classes.txt"

        with open(classes_file, 'w') as f:
            for fruit_class in fruit_classes:
                f.write(f"{fruit_class}\n")

        print(f"Generated {len(fruit_classes)} fruit class labels and saved to: {classes_file}")

        return True

    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        return False

def main():
    """Main function"""
    print("VGG16 Fruits Classifier Model Downloader")
    print("=" * 50)

    if download_model():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Run the Flask app: python app.py")
        print("2. Or use Docker: docker-compose up --build")
        print("3. Test the API at: http://localhost:5000/health")
    else:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()