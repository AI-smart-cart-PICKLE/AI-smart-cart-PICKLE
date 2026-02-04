from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Body, HTTPException
from pydantic import BaseModel, ConfigDict
import os
import io
import sys
import mlflow
import asyncio
import time
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

# [Benchmark Globals]
active_run_id = None
inference_cnt = 0
accumulated_time = 0.0

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
# Request Models
# ==============================
class TrainRequest(BaseModel):
    epochs: int = 10
    experiment_name: str = "manual_trigger"
    model_name: str = "yolov8s.pt"

    # 추가 파라미터(imgsz, mosaic, lr0 등) 허용
    model_config = ConfigDict(extra="allow")

# ==============================
# Background Training Wrapper
# ==============================
async def background_train_wrapper(
    model_name: str,
    epochs: int,
    experiment_name: str,
    **kwargs
):
    global is_training
    try:
        is_training = True
        print(f"[TRAIN] start | model={model_name}, epochs={epochs}, exp={experiment_name}, extras={kwargs}")

        # 동기 함수인 run_training을 별도 스레드에서 실행
        await asyncio.to_thread(
            run_training,
            model_name=model_name,
            epochs=epochs,
            experiment_name=experiment_name,
            **kwargs
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

    # MLflow run_id 기반 모델 다운로드
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

    # [Benchmark] Start Inference Run
    global active_run_id
    try:
        experiment_name = "Jetson_Inference_Benchmark"
        mlflow.set_experiment(experiment_name)
        
        # End any existing run just in case
        mlflow.end_run()
        
        run = mlflow.start_run(run_name=f"inference_session_{int(time.time())}")
        active_run_id = run.info.run_id
        print(f"[MLflow] Benchmark Run Started: {active_run_id} (Exp: {experiment_name})")
        
        mlflow.log_param("platform", "Jetson Orin Nano")
        mlflow.log_param("device", "cuda" if "cuda" in str(os.getenv("CUDA_VISIBLE_DEVICES", "")) else "cpu")
    except Exception as e:
        print(f"[MLflow] Benchmark init failed: {e}")

    # 모델 로드
    try:
        if os.path.exists(MODEL_PATH):
            print(f"[MODEL] Loading {MODEL_PATH}")
            model = YOLO(MODEL_PATH)
            if active_run_id:
                mlflow.log_param("model_loaded", MODEL_PATH)
        else:
            print("[MODEL] best.pt not found → loading yolov8n.pt")
            model = YOLO("yolov8n.pt")
            if active_run_id:
                mlflow.log_param("model_loaded", "yolov8n.pt")
    except Exception as e:
        print(f"[MODEL] load failed: {e}")
        model = YOLO("yolov8n.pt")

    yield
    
    if active_run_id:
        print("[MLflow] Ending Benchmark Run")
        mlflow.end_run()
    
    print("AI Inference Server Shutting Down...")

# ==============================
# FastAPI App (선언 위치 중요: 라우터 등록 전)
# ==============================
app = FastAPI(
    title="Smart Cart AI Inference Server",
    lifespan=lifespan
)

# ==============================
# API Endpoints
# ==============================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "is_training": is_training,
        "benchmark_run_id": active_run_id
    }

@app.get("/models")
def get_available_models():
    return {
        "allowed_base_models": sorted(list(ALLOWED_MODELS)),
        "local_models": [
            f for f in os.listdir(MODEL_LOCAL_DIR)
            if f.endswith(".pt")
        ]
    }

@app.post("/train")
async def train_model(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
):
    global is_training

    if is_training:
        raise HTTPException(status_code=409, detail="Training already in progress")

    if request.model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_name. Allowed: {sorted(ALLOWED_MODELS)}"
        )

    # 파라미터 분리
    req_data = request.model_dump()
    epochs = req_data.pop("epochs")
    experiment_name = req_data.pop("experiment_name")
    model_name = req_data.pop("model_name")
    
    # 백그라운드 작업 추가
    background_tasks.add_task(
        background_train_wrapper,
        model_name=model_name,
        epochs=epochs,
        experiment_name=experiment_name,
        **req_data
    )

    return {
        "message": "Training started",
        "params": request.model_dump()
    }

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
        
        # Log switch event if benchmarking
        if active_run_id:
            mlflow.log_param("switched_model_run_id", run_id)
            
        return {"message": "Model switched successfully", "run_id": run_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    global inference_cnt, accumulated_time
    
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # [Benchmark] Start Timer
        start_time = time.time()

        results = model.predict(image, imgsz=640)

        # [Benchmark] End Timer & Calc
        end_time = time.time()
        duration = end_time - start_time
        
        inference_cnt += 1
        accumulated_time += duration
        
        # 30 프레임마다 로깅
        if inference_cnt % 30 == 0:
            avg_fps = 30 / accumulated_time
            avg_latency_ms = (accumulated_time / 30) * 1000
            
            print(f"[Benchmark] FPS: {avg_fps:.2f} | Latency: {avg_latency_ms:.2f}ms")
            
            if active_run_id:
                try:
                    mlflow.log_metric("fps", avg_fps, step=inference_cnt)
                    mlflow.log_metric("latency_ms", avg_latency_ms, step=inference_cnt)
                except Exception as e:
                    print(f"[MLflow] Log failed: {e}")
            
            accumulated_time = 0.0


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
            "detections": detections,
            "server_fps_check": round(30/accumulated_time, 2) if accumulated_time > 0 and (inference_cnt % 30 == 0) else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Main Execution
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
