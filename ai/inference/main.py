from fastapi import FastAPI
import logging
import os

app = FastAPI(title="Smart Cart AI Inference Server")

@app.get("/")
def read_root():
    return {"message": "AI Inference Server is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/models")
def get_models():
    """Returns a list of available models."""
    models_dir = "models"
    if not os.path.exists(models_dir):
        return {"models": []}
    models = [f for f in os.listdir(models_dir) if f.endswith(".pt")]
    return {"models": models}

# 추후 여기에 YOLO 모델 로드 및 추론 로직 추가
