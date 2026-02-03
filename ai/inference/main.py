from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Body, HTTPException
import os
import io
import sys
import mlflow
import asyncio
from contextlib import asynccontextmanager
from ultralytics import YOLO
from PIL import Image

# ==============================
# Path 설정
# ==============================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from training.train import train as run_training
except ImportError:
    from ai.training.train import train as run_training

# ==============================
# Global State
# ==============================
model = None
is_training = False

MODEL_LOCAL_DIR = "models"
MODEL_FILENAME = "best.pt"
MODEL_PATH = os.path.join(MODEL_LOCAL_DIR, MODEL_FILENAME)

# 허용 모델 화이트리스트
ALLOWED_MODELS = {
    "yolov8n.pt",
    "yolov8s.pt",
    "yolov8m.pt",
    "yolo11n.pt",
    "yolo11s.pt"
}

# ==============================
# Background Training Wrapper
# ==============================
async def background_train_wrapper(
    epochs: int,
    experiment_name: str,
    model_name: str
):
    global is_training
    try:
        is_training = True
        print(f"[TRAIN] start | model={model_name}, epochs={epochs}, exp={experiment_name}")

        await asyncio.to_thread(
            run_training,
            epochs=epochs,
            experiment_name=experiment_name,
            model_name=model_name
        )

        print("[TRAIN] finished")
    except Exception as e:
        print(f"[TRAIN] failed: {e}")
    finally:
        is_training = False

# ==============================
# Lifespan (Startup / Shutdown)
# ==============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model

    print("AI Inference Server Initializing...")

    os.makedirs(MODEL_LOCAL_DIR, exist_ok=True)

    # MLflow 설정
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow.set_tracking_uri(mlflow_uri)

    # ==============================
    # MLflow run_id 기반 모델 다운로드
    # ==============================
    run_id = os.getenv("MODEL_RUN_ID")
    if run_id:
        try:
            print(f"[MODEL] Downloading from MLflow run_id={run_id}")
            mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path=f"weights/{MODEL_FILENAME}",
                dst_path=MODEL_LOCAL_DIR
            )
        except Exception as e:
            print(f"[MODEL] MLflow download failed: {e}")

    # ==============================
    # 모델 로드
    # ==============================
    try:
        if os.path.exists(MODEL_PATH):
            print(f"[MODEL] Loading {MODEL_PATH}")
            model = YOLO(MODEL_PATH)
        else:
            print("[MODEL] best.pt not found → loading yolov8n.pt")
            model = YOLO("yolov8n.pt")
    except Exception as e:
        print(f"[MODEL] load failed: {e}")
        model = YOLO("yolov8n.pt")

    yield
    print("AI Inference Server Shutting Down...")

# ==============================
# FastAPI App
# ==============================
app = FastAPI(
    title="Smart Cart AI Inference Server",
    lifespan=lifespan
)

# ==============================
# Health
# ==============================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "is_training": is_training
    }

# ==============================
# Available Models
# ==============================
@app.get("/models")
def get_available_models():
    return {
        "allowed_base_models": sorted(list(ALLOWED_MODELS)),
        "local_models": [
            f for f in os.listdir(MODEL_LOCAL_DIR)
            if f.endswith(".pt")
        ]
    }

# ==============================
# Train API
# ==============================
@app.post("/train")
async def train_model(
    background_tasks: BackgroundTasks,
    epochs: int = Body(10, embed=True),
    experiment_name: str = Body("manual_trigger", embed=True),
    model_name: str = Body("yolov8s.pt", embed=True)
):
    global is_training

    if is_training:
        raise HTTPException(status_code=409, detail="Training already in progress")

    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_name. Allowed: {sorted(ALLOWED_MODELS)}"
        )

    background_tasks.add_task(
        background_train_wrapper,
        epochs=epochs,
        experiment_name=experiment_name,
        model_name=model_name
    )

    return {
        "message": "Training started",
        "epochs": epochs,
        "experiment": experiment_name,
        "model_name": model_name
    }

# ==============================
# Switch Serving Model (run_id)
# ==============================
@app.post("/model/switch")
def switch_model(run_id: str = Body(..., embed=True)):
    global model

    try:
        print(f"[MODEL] Switching to run_id={run_id}")
        mlflow.artifacts.download_artifacts(
            run_id=run_id,
            artifact_path=f"weights/{MODEL_FILENAME}",
            dst_path=MODEL_LOCAL_DIR
        )

        model = YOLO(MODEL_PATH)

        return {
            "message": "Model switched successfully",
            "run_id": run_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Predict
# ==============================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        results = model.predict(image, imgsz=640)

        detections = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls)
                detections.append({
                    "class": cls,
                    "name": model.names[cls],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()[0]
                })

        return {
            "count": len(detections),
            "detections": detections
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Run (local only)
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
