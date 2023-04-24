from flask import Flask, render_template, request, jsonify
from PIL import Image
from io import BytesIO
import base64
import torch
from transformers import YolosFeatureExtractor, YolosForObjectDetection
import math

app = Flask(__name__)


COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]


# Load YOLO model
feature_extractor = YolosFeatureExtractor.from_pretrained("hustvl/yolos-tiny")
model = YolosForObjectDetection.from_pretrained("hustvl/yolos-tiny")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect_objects", methods=["POST"])
def detect_objects():
    # Receive the image data and decode it
    img_data = request.form["image"]
    img_data = base64.b64decode(img_data.split(",")[-1])
    img = Image.open(BytesIO(img_data))

    # Perform object detection using YOLO model
    inputs = feature_extractor(images=img, return_tensors="pt")
    outputs = model(**inputs)

    # Retrieve logits and bounding boxes from the model output
    logits = outputs.logits
    bboxes = outputs.pred_boxes.sigmoid()

    # Process the results
    logits = torch.softmax(logits, -1).detach().cpu().numpy()
    bboxes = bboxes.detach().cpu().numpy()

    # Remove the extra dimension from logits and bboxes
    logits = logits.squeeze(0)
    bboxes = bboxes.squeeze(0)
  
    # Get the size of the input image
    width, height = img.size
    
    results = []
    confidence_threshold = 0.5
    for logit, bbox in zip(logits, bboxes):
        for class_idx, confidence in enumerate(logit):
            if confidence > confidence_threshold and class_idx < len(COCO_CLASSES):
                center_x, center_y, w, h = bbox
                # Normalize the bounding box coordinates
                x = (center_x - w / 2) * width
                y = (center_y - h / 2) * height
                w = w * width
                h = h * height
                class_name = COCO_CLASSES[class_idx]
                results.append({"class_name": class_name, "confidence": float(confidence), "bbox": [float(x), float(y), float(w), float(h)]})
    

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
