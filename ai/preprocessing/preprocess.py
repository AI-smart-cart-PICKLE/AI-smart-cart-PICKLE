# ai/preprocessing/preprocess.py
import os

DATASET_PATH = "C:/Users/SSAFY/Desktop/smart-cart-detection.v1i.yolov8"


def validate_dataset():
    """
    YOLOv8 데이터셋 최소 전처리(검증)
    - train/images ↔ train/labels 1:1
    - 파일 존재 여부
    """

    img_dir = os.path.join(DATASET_PATH, "train/images")
    lbl_dir = os.path.join(DATASET_PATH, "train/labels")

    if not os.path.isdir(img_dir):
        raise FileNotFoundError("train/images not found")

    if not os.path.isdir(lbl_dir):
        raise FileNotFoundError("train/labels not found")

    imgs = {os.path.splitext(f)[0] for f in os.listdir(img_dir)}
    lbls = {os.path.splitext(f)[0] for f in os.listdir(lbl_dir)}

    diff = imgs ^ lbls
    if diff:
        raise ValueError(f"Image/Label mismatch: {len(diff)} files")

    print("[PREPROCESS] Dataset validation passed")


if __name__ == "__main__":
    validate_dataset()
