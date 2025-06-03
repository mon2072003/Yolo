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

    # Resize to model's expected input size
    img_resized = cv2.resize(img, (640, 640))
    img_input = img_resized / 255.0
    img_input = img_input.transpose(2, 0, 1).astype(np.float32)
    img_input = np.expand_dims(img_input, axis=0)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img_input})

    # استخراج الأصناف (class indices)
    # تأكد من أن هذا يتماشى مع شكل إخراج النموذج لديك
    try:
        # نفترض أن المخرجات [boxes, scores, class_ids]
        class_ids = outputs[2]  # تأكد أن هذا هو المؤشر الصحيح في مخرجاتك
        classes = [int(cls) for cls in class_ids[0]]
    except Exception as e:
        return jsonify({"error": f"Error parsing outputs: {str(e)}", "raw_outputs": [o.tolist() for o in outputs]}), 500

    return jsonify({"classes": classes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
