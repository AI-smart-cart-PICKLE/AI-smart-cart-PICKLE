import time
import requests
import cv2
import os
from collections import Counter, deque
from ultralytics import YOLO

# =========================================================
# 🛒 Smart Cart Edge Agent
# =========================================================
# [실행 가이드]
# 1. 환경 변수 설정 (또는 .env 파일):
#    export BACKEND_URL="https://bapsim.site"
#    export DEVICE_CODE="CART-DEVICE-001"
#    export MODEL_PATH="best.pt"
# 2. 실행:
#    python cart_agent.py
# =========================================================

# 설정
# 엣지 디바이스에서 백엔드 서버 주소 (localhost는 사용 불가)
BACKEND_URL = os.getenv("BACKEND_URL", "https://bapsim.site") 
DEVICE_CODE = os.getenv("DEVICE_CODE", "CART-DEVICE-001")
MODEL_PATH = os.getenv("MODEL_PATH", "best.pt") # 같은 폴더에 두는 것을 권장
CONF_THRESHOLD = 0.5
CAMERA_INDEX = 0

# 안정화 설정 (Global Stability)
# 30FPS 기준, 30프레임(약 1초) 동안 90% 이상 일치하면 전송
WINDOW_SIZE = 30 
STABILIZATION_THRESHOLD = 0.9

def get_global_stabilized_state(buffer):
    """
    버퍼 전체를 분석하여, 전체 상태(Snapshot)가 안정적인지 판단합니다.
    불안정하면 None을 반환합니다.
    """
    # 1. 딕셔너리 리스트를 해시 가능한 튜플 형태로 변환 (Counter 사용을 위해)
    # 예: {'apple': 1, 'spam': 2} -> (('apple', 1), ('spam', 2))
    state_history = []
    for frame_data in buffer:
        # 키(상품명) 순으로 정렬하여 튜플 생성
        items_tuple = tuple(sorted(frame_data.items()))
        state_history.append(items_tuple)
    
    # 2. 가장 많이 등장한 '전체 상태' 찾기
    most_common_state, count = Counter(state_history).most_common(1)[0]
    
    # 3. 그 상태의 점유율 확인
    stability_score = count / len(buffer)
    
    if stability_score >= STABILIZATION_THRESHOLD:
        # 튜플 -> 다시 API 전송용 리스트로 변환
        # most_common_state: (('apple', 1), ('spam', 2))
        inventory = [{"product_name": k, "quantity": v} for k, v in most_common_state]
        return inventory
    
    return None # 아직 흔들리는 중 (안정화 실패)

def run_inference():
    print(f"Loading model: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
    except:
        print("Fallback to yolov8n.pt")
        model = YOLO("yolov8n.pt")
    
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Camera Error")
        return

    detection_buffer = deque(maxlen=WINDOW_SIZE)
    
    # 초기 상태는 None으로 두어, 첫 안정화 성공 시 무조건 전송하도록 함
    last_sync_inventory = None 
    last_sync_time = 0

    print(f"Inference started (Global Sync Mode). Device: {DEVICE_CODE}")
    print(f"Waiting for {STABILIZATION_THRESHOLD*100}% consistency over {WINDOW_SIZE} frames...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: 
                time.sleep(0.1)
                continue

            # 1. 추론
            results = model(frame, conf=CONF_THRESHOLD, verbose=False)
            
            # 2. 현재 프레임 상태 파악
            current_frame_counts = Counter()
            for r in results:
                for box in r.boxes:
                    class_name = model.names[int(box.cls[0])]
                    current_frame_counts[class_name] += 1
            
            # 3. 버퍼에 저장 (빈 카트인 경우도 빈 dict {}로 저장됨)
            detection_buffer.append(dict(current_frame_counts))
            
            # 4. 버퍼가 찼을 때만 판단
            if len(detection_buffer) == WINDOW_SIZE:
                stabilized_inventory = get_global_stabilized_state(detection_buffer)
                
                # 안정화된 결과가 나왔을 때만 로직 수행 (None이면 무시)
                if stabilized_inventory is not None:
                    
                    # 5. 상태 변화가 있거나 하트비트(15초)
                    current_time = time.time()
                    
                    # last_sync_inventory가 초기 상태(None)이거나, 내용이 달라졌을 때
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
                                count = len(stabilized_inventory)
                                print(f"[{time.strftime('%H:%M:%S')}] Synced: {count} types stable. {stabilized_inventory}")
                                last_sync_inventory = stabilized_inventory
                                last_sync_time = current_time
                            else:
                                print(f"[Server Error] {resp.status_code}")
                                
                        except Exception as e:
                            print(f"[Network Error] {e}")
                
                # else: (안정화 안 됨) -> 그냥 넘어감 (화면이 흔들리거나 물건 넣는 중)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        cap.release()

if __name__ == "__main__":
    run_inference()
