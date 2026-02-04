from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
import requests
import os

# 필요하다면 관리자 인증 의존성(Depends) 추가 가능
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# AI 서버 주소 (환경변수 처리)
AI_SERVER_URL = os.getenv("AI_INFERENCE_URL", "http://ai_inference:8000")

class TrainRequest(BaseModel):
    epochs: int = 10
    experiment_name: str = "manual_trigger"
    model_name: str = "yolo11s.pt"  # yolov8n.pt, yolov8s.pt, yolov8m.pt, yolo11n.pt 등
    
    # 추가 파라미터 허용 (mosaic, lr0 등)
    model_config = ConfigDict(extra="allow")

@router.post("/train")
def trigger_training(req: TrainRequest):
    """
    [Admin] 모델 재학습 요청을 AI 서버(CPU)로 중계합니다.
    """
    url = f"{AI_SERVER_URL}/train"
    payload = req.model_dump() # Pydantic v2 권장
    
    print(f"[Admin] Forwarding training request to {url} with {payload}")
    
    try:
        # AI 서버 호출
        resp = requests.post(url, json=payload, timeout=5)
        
        if resp.status_code == 200:
            return resp.json()
        else:
            raise HTTPException(status_code=resp.status_code, detail=f"AI Server Error: {resp.text}")
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="AI Inference Server is unreachable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
