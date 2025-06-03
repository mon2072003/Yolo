from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np
import onnxruntime as ort
from PIL import Image
import cv2

app = Flask(__name__)
CORS(app)

model_path = os.path.join("assets", "best.onnx")

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Load ONNX model
session = ort.InferenceSession(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    try:
        img = Image.open(file.stream).convert('RGB')
    except Exception as e:
        return jsonify({"error": f"Invalid image: {str(e)}"}), 400

    img = np.array(img)

    # Resize image to 640x640 as expected by YOLOv8
    img_resized = cv2.resize(img, (640, 640))
    img_input = img_resized / 255.0  # normalize to [0,1]
    img_input = img_input.transpose(2, 0, 1).astype(np.float32)  # HWC to CHW
    img_input = np.expand_dims(img_input, axis=0)  # Add batch dimension

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img_input})

    # Parse classes from YOLOv8 ONNX output
    # Assume output[0] shape: [1, num_detections, 6] where each row: [x1, y1, x2, y2, conf, class_id]
    output = outputs[0]
    detections = output[0]  # shape: [num_detections, 6]

    classes = []
    for det in detections:
        confidence = det[4]
        if confidence > 0.5:  # apply confidence threshold
            class_id = int(det[5])
            classes.append(class_id)

    return jsonify({"classes": classes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
