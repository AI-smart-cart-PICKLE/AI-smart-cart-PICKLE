# ==============================
# YOLOv8 Training Script (with MLflow)
# ==============================

import os
import mlflow
from ultralytics import YOLO

# --- [필수] Windows OpenMP 충돌 방지 ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# ==============================
# Path / Env
# ==============================
DEFAULT_DATASET_PATH = "/data/dataset"
DATASET_PATH = os.getenv("DATASET_PATH", DEFAULT_DATASET_PATH)
DATA_YAML = os.path.join(DATASET_PATH, "data.yaml")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
DEFAULT_EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    "smart-cart-training"
)

# ==============================
# Train Function
# ==============================
def train(
    *,
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 16,
    device: object = 0,
    data_yaml: str = DATA_YAML,
    project: str = "/data/runs/train",
    name: str = "mlflow_run",
    experiment_name: str = DEFAULT_EXPERIMENT_NAME,
    model_name: str = "yolov8s.pt"
):
    """
    YOLOv8 학습 + MLflow 로깅

    Args:
        model_name: 사전학습 모델 (.pt)
        experiment_name: MLflow experiment name
    """

    # ==============================
    # MLflow Init
    # ==============================
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(experiment_name)

    print(f"[MLflow] URI        : {MLFLOW_TRACKING_URI}")
    print(f"[MLflow] Experiment : {experiment_name}")
    print(f"[Training] Model    : {model_name}")

    # ==============================
    # Load Model
    # ==============================
    model = YOLO(model_name)

    # ==============================
    # MLflow Run
    # ==============================
    mlflow.end_run()  # 혹시 남아있는 run 정리
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"[MLflow] Run ID: {run_id}")

        # ==============================
        # Device Check
        # ==============================
        import torch
        if device == 0 and not torch.cuda.is_available():
            print("[Warning] CUDA not available → CPU fallback")
            device = "cpu"

        # ==============================
        # Log Params
        # ==============================
        mlflow.log_params({
            "model_name": model_name,
            "epochs": epochs,
            "imgsz": imgsz,
            "batch": batch,
            "device": device,
            "data_yaml": data_yaml
        })

        print("[Training] Start")

        # ==============================
        # Train
        # ==============================
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

            # --- Stability ---
            amp=True,
            deterministic=True,
            seed=0,

            project=project,
            name=name,
            exist_ok=True
        )

        # ==============================
        # Metrics
        # ==============================
        metrics = {
            "mAP50": float(results.box.map50),
            "mAP50_95": float(results.box.map),
            "fitness": float(results.fitness)
        }
        mlflow.log_metrics(metrics)

        print(f"[MLflow] Metrics: {metrics}")

        # ==============================
        # Artifacts
        # ==============================
        best_model_path = os.path.join(
            results.save_dir,
            "weights",
            "best.pt"
        )

        if not os.path.exists(best_model_path):
            raise FileNotFoundError(
                f"best.pt not found at {best_model_path}"
            )

        # 🔑 AI 서버와 약속된 경로
        mlflow.log_artifact(
            best_model_path,
            artifact_path="weights"
        )

        # Optional: confusion matrix
        confusion_matrix = os.path.join(
            results.save_dir,
            "confusion_matrix.png"
        )
        if os.path.exists(confusion_matrix):
            mlflow.log_artifact(
                confusion_matrix,
                artifact_path="plots"
            )

        print("[MLflow] Artifacts uploaded")

        return run_id


# ==============================
# Local Run
# ==============================
if __name__ == "__main__":
    train()
