# ==============================
# YOLOv8 Training Script (with MLflow)
# ==============================

import os
import mlflow
from ultralytics import YOLO

# --- [필수] Windows OpenMP 충돌 방지 ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- 경로 설정 (환경변수 우선, 없으면 로컬 기본값) ---
DEFAULT_DATASET_PATH = "/data/dataset"
DATASET_PATH = os.getenv("DATASET_PATH", DEFAULT_DATASET_PATH)
DATA_YAML = os.path.join(DATASET_PATH, "data.yaml")

# --- MLflow 설정 ---
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "smart-cart-training")

def train(
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 16,
    device: object = 0,
    data_yaml: str = DATA_YAML,
    project: str = "/data/runs/train",
    name: str = "mlflow_exp",
    experiment_name: str = EXPERIMENT_NAME
):
    """
    YOLOv8 학습 및 MLflow 로깅 함수
    """
    # 1. MLflow 초기화
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(experiment_name)
    print(f"[MLflow] Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"[MLflow] Experiment: {experiment_name}")

    # 2. 사전학습 모델 로드
    model_name = "yolov8s.pt"
    model = YOLO(model_name)

    # 3. MLflow Run 시작
    mlflow.end_run() # 안전장치: 혹시라도 닫히지 않은 이전 Run 강제 종료
    with mlflow.start_run() as run:
        print(f"[MLflow] Run ID: {run.info.run_id}")
        
        # Check CUDA availability
        import torch
        if device == 0 and not torch.cuda.is_available():
            print("[Warning] CUDA not available. Falling back to CPU.")
            device = 'cpu'
            
        # 파라미터 로깅
        mlflow.log_params({
            "model": model_name,
            "data": data_yaml,
            "epochs": epochs,
            "imgsz": imgsz,
            "batch": batch,
            "device": device
        })

        print("Starting training...")
        
        # 4. 학습 실행
        # project='runs/train', name='mlflow_run'으로 지정하여 경로 예측 가능하게 설정
        results = model.train(
            data=data_yaml,
            imgsz=imgsz,
            epochs=epochs,
            batch=batch,
            device=device,
            workers=0,

            # --- Augmentation ---
            mosaic=1.0,
            mixup=0.2,
            fliplr=0.5,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,

            # --- 안정성 옵션 ---
            amp=True,
            deterministic=True,
            seed=0,
            
            project=project,
            name=name,
            exist_ok=True
        )

        # 5. 결과 지표 로깅
        # YOLOv8의 results 객체에서 지표 추출
        metrics = {
            "mAP50": results.box.map50,
            "mAP50-95": results.box.map,
            "fitness": results.fitness,
            # 필요한 경우 loss 등 추가 가능 (results.results_dict 확인)
        }
        mlflow.log_metrics(metrics)
        print(f"[MLflow] Logged metrics: {metrics}")

        # 6. 모델 아티팩트 업로드 (MinIO)
        # best.pt 모델 파일 경로
        best_model_path = os.path.join(results.save_dir, "weights", "best.pt")
        
        if os.path.exists(best_model_path):
            print(f"Uploading model artifact: {best_model_path}")
            mlflow.log_artifact(best_model_path, artifact_path="weights")
            
            # (옵션) 혼동 행렬 등 시각화 이미지도 업로드
            confusion_matrix = os.path.join(results.save_dir, "confusion_matrix.png")
            if os.path.exists(confusion_matrix):
                mlflow.log_artifact(confusion_matrix, artifact_path="plots")
                
            print("[MLflow] Upload complete.")
        else:
            print(f"[Warning] Model file not found at {best_model_path}")
            
        return run.info.run_id

if __name__ == "__main__":
    train()
