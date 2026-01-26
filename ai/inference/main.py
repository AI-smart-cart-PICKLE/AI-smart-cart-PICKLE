from fastapi import FastAPI, File, UploadFile
import mlflow
import os
import shutil
from ultralytics import YOLO
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 환경 변수 설정
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
MODEL_PATH = "/tmp/best.pt"

# 전역 모델 변수
model = None

@app.on_event("startup")
def load_model():
    global model
    try:
        logger.info(f"Connecting to MLflow at {MLFLOW_TRACKING_URI}")
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        
        # 1. 최신 실험의 최신 Run 찾기
        experiment_name = "YOLO_Mock_Training"
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if experiment:
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string="status = 'FINISHED'",
                order_by=["start_time DESC"],
                max_results=1
            )
            
            if not runs.empty:
                run_id = runs.iloc[0].run_id
                artifact_path = "models/best.pt" # mock_train.py에서 저장한 경로
                
                logger.info(f"Downloading model from run: {run_id}")
                local_dir = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path=artifact_path)
                
                # 다운로드된 파일 위치 확인 및 이동
                if os.path.isfile(local_dir):
                    shutil.copy(local_dir, MODEL_PATH)
                else:
                    # 폴더로 다운로드된 경우
                    src_file = os.path.join(local_dir, "best.pt")
                    if os.path.exists(src_file):
                        shutil.copy(src_file, MODEL_PATH)
                
                logger.info(f"Model saved to {MODEL_PATH}")
                model = YOLO(MODEL_PATH)
                logger.info("YOLO model loaded successfully from MLflow.")
                return

        logger.warning("No model found in MLflow. Loading default yolov8n.pt")
        model = YOLO("yolov8n.pt")
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        logger.info("Falling back to default yolov8n.pt")
        model = YOLO("yolov8n.pt")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        return {"error": "Model not loaded"}, 503
    
    # 임시 저장 및 추론
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    results = model(temp_path)
    
    # 결과 파싱 (간단 예시)
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy.tolist()
            })
            
    return {"detections": detections}