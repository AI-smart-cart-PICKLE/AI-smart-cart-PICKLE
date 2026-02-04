import time
import requests
import cv2
import os
import json
import uuid
import numpy as np
from collections import Counter, deque
from datetime import datetime
from threading import Thread
from ultralytics import YOLO
import boto3

BACKEND_URL = os.getenv("BACKEND_URL", "https://bapsim.site")
DEVICE_CODE = os.getenv("DEVICE_CODE", "CART-DEVICE-001")
MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")
CONF_THRESHOLD = 0.5
CAMERA_INDEX = 0
WINDOW_SIZE = 30
STABILIZATION_THRESHOLD = 0.9

# Uncertain image collection configuration
UNCERTAIN_THRESHOLD = float(os.getenv("UNCERTAIN_CONFIDENCE_THRESHOLD", "0.65"))
UPLOAD_INTERVAL = float(os.getenv("UNCERTAIN_UPLOAD_INTERVAL", "5"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "https://bapsim.site")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")

# Initialize S3 client for uncertain image uploads
try:
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        verify=False  # For self-signed certificates
    )
    print(f"[S3] Initialized client for uncertain images: {MINIO_ENDPOINT}")
except Exception as e:
    print(f"[S3] Failed to initialize client: {e}")
    s3_client = None

def get_global_stabilized_state(buffer):
    state_history = []
    for frame_data in buffer:
        items_tuple = tuple(sorted(frame_data.items()))
        state_history.append(items_tuple)

    most_common_state, count = Counter(state_history).most_common(1)[0]
    stability_score = count / len(buffer)

    if stability_score >= STABILIZATION_THRESHOLD:
        inventory = [{"product_name": k, "quantity": v} for k, v in most_common_state]
        return inventory

    return None

def has_low_confidence(detections, threshold):
    """Check if any detection has confidence below threshold"""
    return any(d['confidence'] < threshold for d in detections)

def detections_changed(current_detections, last_detections, conf_threshold=0.1):
    """Check if object composition has changed significantly"""
    if not last_detections:
        return True

    # Compare class counts
    curr_classes = Counter([d['name'] for d in current_detections])
    last_classes = Counter([d['name'] for d in last_detections])

    if curr_classes != last_classes:
        return True  # Different objects detected

    # Compare average confidence
    curr_conf = np.mean([d['confidence'] for d in current_detections]) if current_detections else 0
    last_conf = np.mean([d['confidence'] for d in last_detections]) if last_detections else 0

    return abs(curr_conf - last_conf) > conf_threshold

def upload_to_s3_async(image_bytes, metadata, device_code):
    """Upload image and metadata to S3 in background thread"""
    def _upload():
        try:
            timestamp = datetime.utcnow()
            file_id = f"{timestamp.strftime('%Y-%m-%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            prefix = f"uncertain-images/{device_code}"

            # Upload image
            s3_client.put_object(
                Bucket='smart-cart-mlops',
                Key=f"{prefix}/{file_id}.jpg",
                Body=image_bytes,
                ContentType='image/jpeg'
            )

            # Upload metadata
            s3_client.put_object(
                Bucket='smart-cart-mlops',
                Key=f"{prefix}/{file_id}.json",
                Body=json.dumps(metadata, indent=2),
                ContentType='application/json'
            )

            print(f"[S3] Uploaded uncertain image: {file_id}")
        except Exception as e:
            print(f"[S3] Upload failed: {e}")

    if s3_client:
        Thread(target=_upload, daemon=True).start()
    else:
        print("[S3] Upload skipped - S3 client not initialized")

def run_inference():
    try:
        model = YOLO(MODEL_PATH)
    except:
        model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        return

    detection_buffer = deque(maxlen=WINDOW_SIZE)
    last_sync_inventory = None
    last_sync_time = 0

    # Uncertain image upload tracking
    last_uncertain_upload = 0
    last_uploaded_detections = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            results = model(frame, conf=CONF_THRESHOLD, verbose=False)

            current_frame_counts = Counter()
            detections = []
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])

                    current_frame_counts[class_name] += 1

                    # Build detection list for uncertain image upload
                    detections.append({
                        "class": class_id,
                        "name": class_name,
                        "confidence": confidence,
                        "bbox": box.xyxy[0].tolist()
                    })

            # Check for uncertain detections and upload if needed
            current_time = time.time()
            should_upload = (
                has_low_confidence(detections, UNCERTAIN_THRESHOLD) and
                current_time - last_uncertain_upload > UPLOAD_INTERVAL and
                detections_changed(detections, last_uploaded_detections)
            )

            if should_upload:
                # Convert frame to JPEG bytes
                _, buffer = cv2.imencode('.jpg', frame)
                image_bytes = buffer.tobytes()

                # Build metadata
                metadata = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "device_code": DEVICE_CODE,
                    "detections": detections,
                    "reason": "low_confidence",
                    "threshold": UNCERTAIN_THRESHOLD
                }

                # Upload asynchronously
                upload_to_s3_async(image_bytes, metadata, DEVICE_CODE)

                # Update tracking variables
                last_uncertain_upload = current_time
                last_uploaded_detections = detections.copy()

            detection_buffer.append(dict(current_frame_counts))

            if len(detection_buffer) == WINDOW_SIZE:
                stabilized_inventory = get_global_stabilized_state(detection_buffer)

                if stabilized_inventory is not None:
                    current_time = time.time()

                    if (stabilized_inventory != last_sync_inventory) or (current_time - last_sync_time > 15):
                        try:
                            resp = requests.post(
                                f"{BACKEND_URL}/api/carts/sync-by-device",
                                json={
                                    "device_code": DEVICE_CODE,
                                    "items": stabilized_inventory
                                },
                                timeout=2
                            )
                            if resp.status_code == 200:
                                last_sync_inventory = stabilized_inventory
                                last_sync_time = current_time

                        except Exception:
                            pass

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

if __name__ == "__main__":
    run_inference()