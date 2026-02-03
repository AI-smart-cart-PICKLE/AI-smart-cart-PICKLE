import time
import requests
import cv2
import os
from collections import Counter, deque
from ultralytics import YOLO

BACKEND_URL = os.getenv("BACKEND_URL", "https://bapsim.site") 
DEVICE_CODE = os.getenv("DEVICE_CODE", "CART-DEVICE-001")
MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")
CONF_THRESHOLD = 0.5
CAMERA_INDEX = 0
WINDOW_SIZE = 30 
STABILIZATION_THRESHOLD = 0.9

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

    try:
        while True:
            ret, frame = cap.read()
            if not ret: 
                time.sleep(0.1)
                continue

            results = model(frame, conf=CONF_THRESHOLD, verbose=False)
            
            current_frame_counts = Counter()
            for r in results:
                for box in r.boxes:
                    class_name = model.names[int(box.cls[0])]
                    current_frame_counts[class_name] += 1
            
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