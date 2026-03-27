import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image

# ==========================================
# 1. CONFIGURATION
# ==========================================
# If in VS Code, make sure this file is in the same folder as your script
MODEL_NAME = 'final_model_v3.keras'
CLASS_NAMES = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

# ==========================================
# 2. THE "NO-FAIL" MODEL LOADER
# ==========================================
def load_my_model(path):
    # Check if the file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find {path} in the current directory.")

    try:
        # Strategy A: Standard Load
        # We use compile=False because we only need the model for prediction
        model = tf.keras.models.load_model(path, compile=False)
        print("🚀 Model loaded successfully using standard loader.")
        return model
    except Exception:
        # Strategy B: HDF5 Bypass (Fixes the Colab/VS Code Zip error)
        print("⚠️ Detected HDF5 format mismatch. Applying bypass...")
        import h5py
        with h5py.File(path, 'r') as f:
            model = tf.keras.models.load_model(f, compile=False)
        print("🚀 Model loaded successfully using HDF5 bypass.")
        return model

# ==========================================
# 3. EXACT PREPROCESSING (The "Sync" Logic)
# ==========================================
def prepare_image(image_path):
    # 1. Load as RGB (Fixes the BGR/Color swap issue)
    img = Image.open(image_path).convert('RGB')
    
    # 2. Square Center Crop (Prevents stretching the cat into a horse shape)
    w, h = img.size
    side = min(w, h)
    left = (w - side) / 2
    top = (h - side) / 2
    img = img.crop((left, top, left + side, top + side))
    
    # 3. High-Quality Resize (Matches CIFAR-10 training patterns)
    img = img.resize((32, 32), Image.Resampling.LANCZOS)
    
    # 4. Normalize (Must be 1/255.0 to match your training script)
    img_arr = np.array(img) / 255.0
    
    # 5. Add Batch Dimension (1, 32, 32, 3)
    return img_arr.reshape(1, 32, 32, 3), img

# ==========================================
# 4. EXECUTION
# ==========================================
try:
    # Load model once
    my_model = load_my_model(MODEL_NAME)

    # List of images to test - Update these names to match your files!
    test_images = ['cat_capture_0.png', 'airplane.png', 'truck.png', 'bird.png']

    for img_name in test_images:
        if os.path.exists(img_name):
            # Process
            processed_tensor, original_crop = prepare_image(img_name)
            
            # Predict
            # Since your training used 'from_logits=True', we must apply Softmax
            raw_logits = my_model.predict(processed_tensor, verbose=0)
            probabilities = tf.nn.softmax(raw_logits[0]).numpy()
            
            # Get Results
            idx = np.argmax(probabilities)
            confidence = probabilities[idx] * 100
            label = CLASS_NAMES[idx].upper()

            # Output
            print(f"Result for {img_name}: {label} ({confidence:.2f}%)")
            
            # Show Image
            plt.figure(figsize=(2,2))
            plt.imshow(original_crop)
            plt.title(f"{label} {confidence:.1f}%")
            plt.axis('off')
            plt.show()
        else:
            print(f"Skipping {img_name}: File not found.")

except Exception as e:
    print(f"FATAL ERROR: {e}")