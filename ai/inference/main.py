from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Body, HTTPException
import logging
import os
import io
import sys
import mlflow
import asyncio
from contextlib import asynccontextmanager
from ultralytics import YOLO
from PIL import Image

# Add parent directory to path to import training module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from training.train import train as run_training
except ImportError:
    # Fallback if running from root or different context
    from ai.training.train import train as run_training

# 전역 변수로 모델 및 학습 상태 관리
model = None
is_training = False
MODEL_LOCAL_DIR = "models"
MODEL_FILENAME = "best.pt"
MODEL_PATH = os.path.join(MODEL_LOCAL_DIR, MODEL_FILENAME)

async def background_train_wrapper(epochs: int, experiment_name: str):
    """
    학습 상태 플래그를 안전하게 관리하며 백그라운드 학습을 수행하는 래퍼 함수
    """
    global is_training
    try:
        is_training = True
        print(f"Background training started: {experiment_name}")
        # 동기 함수인 학습 로직을 별도 스레드에서 실행하여 이벤트 루프 차단 방지
        await asyncio.to_thread(run_training, epochs=epochs, experiment_name=experiment_name)
        print(f"Background training finished: {experiment_name}")
    except Exception as e:
        print(f"Background training failed: {str(e)}")
    finally:
        is_training = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 시작 시 모델 로드 및 종료 시 정리 로직
    """
    global model
    print("AI Inference Server Initializing...")
    
    # models 디렉토리 보장
    if not os.path.exists(MODEL_LOCAL_DIR):
        os.makedirs(MODEL_LOCAL_DIR)

    # MLflow 설정
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow.set_tracking_uri(mlflow_uri)

    # 1. MLflow에서 모델 다운로드 시도 (MODEL_RUN_ID 환경변수가 있을 경우)
    run_id = os.getenv("MODEL_RUN_ID")
    if run_id:
        try:
            print(f"Attempting to download model from MLflow run: {run_id}")
            # 'weights/best.pt' 경로의 아티팩트를 다운로드
            download_path = mlflow.artifacts.download_artifacts(
                run_id=run_id, 
                artifact_path=f"weights/{MODEL_FILENAME}",
                dst_path=MODEL_LOCAL_DIR
            )
            print(f"Model downloaded to: {download_path}")
        except Exception as e:
            print(f"Failed to download model from MLflow: {e}")

    # 2. 모델 파일 로드 (로컬에 있으면 로드, 없으면 기본 모델 사용)
    try:
        if os.path.exists(MODEL_PATH):
            print(f"Loading custom model from {MODEL_PATH}")
            model = YOLO(MODEL_PATH)
        else:
            print(f"Custom model not found at {MODEL_PATH}. Loading default yolov8n.pt")
            model = YOLO("yolov8n.pt")
    except Exception as e:
        print(f"Error loading model: {e}")
        # 최후의 수단으로 기본 모델 강제 로드
        model = YOLO("yolov8n.pt")

    yield
    print("AI Inference Server Shutting Down...")

app = FastAPI(title="Smart Cart AI Inference Server", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "AI Inference Server is running"}

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "model_loaded": model is not None,
        "is_training": is_training
    }

@app.get("/models")
def get_models():
    if not os.path.exists(MODEL_LOCAL_DIR):
        return {"models": []}
    models = [f for f in os.listdir(MODEL_LOCAL_DIR) if f.endswith(".pt")]
    return {"models": models}

@app.post("/train")
async def train_model(
    background_tasks: BackgroundTasks,
    epochs: int = Body(1, embed=True),
    experiment_name: str = Body("manual_trigger_test", embed=True)
):
    global is_training
    if is_training:
        raise HTTPException(status_code=409, detail="Training is already in progress.")
    
    background_tasks.add_task(background_train_wrapper, epochs=epochs, experiment_name=experiment_name)
    return {"message": "Training started in background", "epochs": epochs, "experiment": experiment_name}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not model:
        return {"error": "Model not initialized"}

    try:
        # 이미지 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # YOLO 추론
        # imgsz는 학습 시와 동일하게 640 권장
        results = model.predict(image, imgsz=640)

        # 결과 파싱
        detections = []
        for result in results:
            for box in result.boxes:
                detections.append({
                    "class": int(box.cls),
                    "name": model.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()[0] # [x1, y1, x2, y2]
                })

        return {
            "count": len(detections),
            "detections": detections
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)