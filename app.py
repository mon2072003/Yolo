from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO

app = Flask(_name_)
CORS(app)

# Correct file path handling
model_path = r"C:\Users\CS\PycharmProjects\my_vistor_model\assets\best.onnx"

# Check if file exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Load the trained YOLOv8 model
model = YOLO(model_path,task="detect")

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    img = Image.open(file.stream)

    # Run inference
    results = model(img)

    # Parse results
    detections = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
            conf = float(box.conf[0])  # Confidence
            cls = int(box.cls[0])  # Class index
            detections.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "conf": conf, "class": cls})
    classes = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])  # Class index
            classes.append(cls)
    return jsonify({"classes": classes})

if _name_ == '_main_':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
