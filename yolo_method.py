from ultralytics import YOLO
import cv2
import numpy
import base64
import os
from datetime import datetime

def find_flower_yolo(b64img: str) -> dict:
    """
    Detect flowers using YOLOv8 model and return processed image with bounding boxes and coordinates.
    """

    # Decode the Base64 image
    image_array = numpy.frombuffer(base64.b64decode(b64img), numpy.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Failed to decode image from Base64 input.")

    if not os.path.exists("YOLOv8-str-flower-model.pt"):
        raise FileNotFoundError("Model file not found")

    # Load the YOLO model
    model = YOLO("YOLOv8-str-flower-model.pt")

    # Run inference
    results = model(image, conf=0.3)

    # Extract bounding boxes and normalize coordinates
    h, w, _ = image.shape
    normalized_coords = []

    for box in results[0].boxes.xyxy.cpu().numpy():
        x_min, y_min, x_max, y_max = map(float, box)
        normalized_coords.append({
            "x": round((x_min + x_max) / (2 * w), 4),  # Center x-coordinate (normalized)
            "y": round((y_min + y_max) / (2 * h), 4)   # Center y-coordinate (normalized)
        })

        # Draw bounding boxes on the image
        cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

    # Save processed image
    os.makedirs("yolo_processed_img", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"yolo_processed_img/processed_image_{timestamp}"
    image_path = f"{filename}.png"
    cv2.imwrite(image_path, image)

    # Save bounding box data to a .txt file
    txt_path = f"{filename}.txt"
    with open(txt_path, "w") as f:
        for coord in normalized_coords:
            f.write(f"{coord['x']:.6f}, {coord['y']:.6f}\n")

    # Convert processed image to Base64
    _, buffer = cv2.imencode(".png", image)
    result_base64 = base64.b64encode(buffer).decode("utf-8")

    # Return JSON response
    return {
        "status": 200,
        "image": f"data:image/png;base64,{result_base64}",
        "imageResult": normalized_coords
    }
