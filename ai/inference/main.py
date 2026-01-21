from fastapi import FastAPI
import logging

app = FastAPI(title="Smart Cart AI Inference Server")

@app.get("/")
def read_root():
    return {"message": "AI Inference Server is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# 추후 여기에 YOLO 모델 로드 및 추론 로직 추가
