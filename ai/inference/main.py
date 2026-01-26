import os
import shutil
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO

app = FastAPI()

# 전역 변수 선언
model = None

@app.on_event("startup")
def load_model():
    """서버 시작 시 모델을 전역 변수에 로드하여 참조 충돌을 방지합니다."""
    global model
    model_path = "models/best.pt"
    if os.path.exists(model_path):
        model = YOLO(model_path)

@app.get("/health")
def health():
    # 전역 변수 model 참조
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 전역 변수 참조 확인
    if model is None:
        return {"error": "Model not loaded"}, 503
    
    # 임시 저장 및 추론
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # YOLO 추론 (동기 함수이므로 루프 차단 주의가 필요하나 로직은 유지)
    results = model(temp_path)

    # 결과 파싱
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy.tolist()
            })
            
    # 파일 정리 로직 추가 (내용 유지하며 충돌만 방지)
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return {"detections": detections}

@app.get("/models")
def get_models():
    """Returns a list of available models."""
    models_dir = "models"
    if not os.path.exists(models_dir):
        return {"models": []}
    models = [f for f in os.listdir(models_dir) if f.endswith(".pt")]
    return {"models": models}