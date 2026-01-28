import cv2
import torch
from ultralytics import YOLO

# =========================
# 설정
# =========================
MODEL_PATH = "/home/jetson/cart/weights/best.pt"
CAMERA_INDEX = 0
IMG_SIZE = 640          # yolov8s 기준 권장
CONF_THRES = 0.4
USE_HALF = True         # Jetson GPU에서 권장

# =========================
# GPU / 모델 초기화
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO(MODEL_PATH)
model.to(device)

if USE_HALF and device == "cuda":
    model.model.half()

# 워밍업 (첫 추론 지연 방지)
dummy = torch.zeros((1, 3, IMG_SIZE, IMG_SIZE), device=device)
if USE_HALF and device == "cuda":
    dummy = dummy.half()
with torch.no_grad():
    model(dummy)

# =========================
# 카메라 초기화
# =========================
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    raise RuntimeError("카메라 열기 실패")

# =========================
# 실시간 추론 루프
# =========================
with torch.no_grad():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO 추론
        results = model(
            frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRES,
            device=device,
            verbose=False
        )

        # 결과 시각화
        annotated = results[0].plot()

        cv2.imshow("YOLOv8s Realtime", annotated)

        # q 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# =========================
# 종료 처리
# =========================
cap.release()
cv2.destroyAllWindows()

