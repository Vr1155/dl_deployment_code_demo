import streamlit as st
import requests
from PIL import Image
import io

# Configure page
st.set_page_config(
    page_title="Cat vs Dog Classifier",
    page_icon="🐱",
    layout="wide"
)

# App title and description
st.title("🐱 vs 🐶 Cat vs Dog Classifier")
st.markdown("Upload an image of a cat or dog and get AI-powered classification results!")

# Sidebar for API configuration
st.sidebar.header("Configuration")
api_host = st.sidebar.text_input("API Host", value="167.172.27.72")
api_port = st.sidebar.number_input("API Port", value=5001, min_value=1, max_value=65535)
api_url = f"http://{api_host}:{api_port}"

# Add API type indicator
container_status = st.sidebar.empty()
if api_host == "167.172.27.72" and api_port == 5001:
    container_status.info("☁️ Using Digital Ocean Docker API")
elif api_port == 5002:
    container_status.info("🐳 Using Local Docker API")
elif api_port == 5001:
    container_status.info("🐍 Using Local Flask API")
else:
    container_status.info("🔧 Using Custom API")

# Test API connection
st.sidebar.subheader("API Status")
try:
    health_response = requests.get(f"{api_url}/health", timeout=5)
    if health_response.status_code == 200:
        health_data = health_response.json()
        if health_data.get('model_loaded'):
            st.sidebar.success("✅ API Connected & Model Loaded")
        else:
            st.sidebar.warning("⚠️ API Connected but Model Not Loaded")
    else:
        st.sidebar.error("❌ API Connection Failed")
except requests.exceptions.RequestException:
    st.sidebar.error("❌ Cannot Connect to API")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Upload Image")
    uploaded_file = st.file_uploader(
        "Choose a cat or dog image...",
        type=["jpg", "jpeg", "png", "bmp", "gif"],
        help="Upload an image of a cat or dog to classify"
    )

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Show image details
        st.caption(f"Image size: {image.size}")
        st.caption(f"Image mode: {image.mode}")

with col2:
    st.header("Classification Results")

    if uploaded_file is not None:
        # Classify button
        if st.button("Classify Pet", type="primary"):
            with st.spinner("Analyzing image..."):
                try:
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)

                    # Send image to Flask backend for prediction
                    files = {"image": uploaded_file}
                    response = requests.post(
                        f"{api_url}/predict",
                        files=files,
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()

                        if result.get("success"):
                            # Show top prediction prominently
                            top_pred = result["top_prediction"]

                            # Add emoji for the prediction
                            emoji = "🐱" if top_pred['class'] == 'Cat' else "🐶"
                            st.success(f"**{emoji} Prediction: {top_pred['class']}**")

                            # Model info
                            if "model" in result:
                                st.info(f"Model: {result['model']}")

                        else:
                            st.error(f"Prediction failed: {result.get('error', 'Unknown error')}")

                    elif response.status_code == 400:
                        error_data = response.json()
                        st.error(f"Bad request: {error_data.get('error', 'Invalid input')}")

                    else:
                        st.error(f"Server error: {response.status_code}")

                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the API. Please check if the Flask app is running.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload an image to get started.")

# Footer with additional information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Model Info")
    if st.button("Get Model Details"):
        try:
            model_response = requests.get(f"{api_url}/model/info", timeout=10)
            if model_response.status_code == 200:
                model_info = model_response.json()
                st.json(model_info)
            else:
                st.error("Failed to get model information")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.subheader("About the Model")
    st.markdown("""
    This is a **VGG16-based binary classifier** trained to distinguish between cats and dogs.

    **Model Details:**
    - Architecture: VGG16 (transfer learning)
    - Classes: Cat, Dog
    - Input size: 150x150 pixels
    - Binary classification output
    - **Deployment**: Running in Docker container (Ubuntu 22.04)
    - **Source**: Hugging Face (carlosaguayo/cats_vs_dogs)
    """)

with col3:
    st.subheader("Tips for Best Results")
    st.markdown("""
    - Use clear, well-lit images
    - Single cat or dog per image works best
    - Images should show the animal clearly
    - Supported formats: PNG, JPG, JPEG, GIF, BMP
    - Works best with images at least 150x150 pixels
    """)