# ==============================
# YOLOv8 Training Script (Stable)
# ==============================

import os

# --- [필수] Windows OpenMP 충돌 방지 ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO

# --- 경로 설정 ---
DATASET_PATH = "C:/Users/SSAFY/Desktop/smart-cart-detection.v1i.yolov8"
DATA_YAML = f"{DATASET_PATH}/data.yaml"

def train():
    """
    YOLOv8 정상 학습 함수
    - GPU 사용
    - on-the-fly augmentation
    - Windows OpenMP 이슈 회피
    """

    # 1. 사전학습 모델 로드
    model = YOLO("yolov8s.pt")

    # 2. 학습 실행
    model.train(
        data=DATA_YAML,
        imgsz=640,
        epochs=50,
        batch=16,
        device=0,          # RTX 4050
        workers=8,

        # --- Augmentation (YOLO 내부) ---
        mosaic=1.0,
        mixup=0.2,
        fliplr=0.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,

        # --- 안정성 옵션 ---
        amp=True,          # Mixed Precision
        deterministic=True,
        seed=0,
    )

if __name__ == "__main__":
    train()
