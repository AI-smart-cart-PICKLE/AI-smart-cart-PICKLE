import sys
import time
import logging
import cv2
import numpy as np
from ultralytics import YOLO

# 1. 로그 설정 (Docker 로그에서 보기 위함)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # 표준 출력으로 내보내야 도커 로그에 찍힘
)
logger = logging.getLogger(__name__)

def check_system_info():
    """시스템 환경 및 라이브러리 버전 확인"""
    logger.info(f"🐍 Python Version: {sys.version.split()[0]}")
    logger.info(f"📷 OpenCV Version: {cv2.__version__}")
    
    # YOLO 체크
    try:
        logger.info("🤖 Loading YOLOv8n model... (First time might download weights)")
        # .gitignore에 의해 로컬에 모델이 없어도, 실행 시 자동으로 다운로드 받습니다.
        model = YOLO('yolov8n.pt')
        logger.info("✅ YOLO model loaded successfully!")
        return model
    except Exception as e:
        logger.error(f"❌ Failed to load YOLO model: {e}")
        return None

def test_inference(model):
    """카메라 없이 가상의 이미지로 추론 테스트"""
    if model is None:
        return

    try:
        # 640x480 검은색 빈 이미지 생성
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 추론 실행
        results = model(dummy_frame, verbose=False)
        logger.info(f"✅ Inference Test Passed! Detected objects: {len(results[0].boxes)}")
    except Exception as e:
        logger.error(f"❌ Inference Test Failed: {e}")

def main():
    logger.info("🚀 Starting Autonomous Driving System (TEST MODE)")
    
    # 1. 환경 점검
    model = check_system_info()
    
    # 2. AI 동작 테스트 (카메라 연결 안 돼 있어도 통과해야 함)
    test_inference(model)

    # 3. 메인 루프 (컨테이너가 죽지 않게 유지)
    logger.info("🔄 Entering main loop. Waiting for updates...")
    
    count = 0
    while True:
        try:
            # 5초마다 생존 신고 (로그가 너무 많이 쌓이지 않게 조절)
            if count % 5 == 0:
                logger.info(f"❤️ System is alive... (Uptime: {count}s)")
            
            # 여기에 실제 주행 로직이나 카메라 읽기 코드가 들어갈 예정
            # ret, frame = cap.read() ...
            
            time.sleep(1)
            count += 1
            
        except KeyboardInterrupt:
            logger.info("🛑 System stopping...")
            break
        except Exception as e:
            logger.error(f"⚠️ Error in main loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()