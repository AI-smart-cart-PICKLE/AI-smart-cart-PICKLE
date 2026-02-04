# Jetson Orin Nano (JetPack 5/6) 및 일반 플랫폼 호환 이미지
# Jetson: JetPack + CUDA + PyTorch 사전 설치된 베이스 이미지 사용
# AMD64/ARM64: Ultralytics 공식 이미지 (PyTorch, YOLO 포함)
FROM ultralytics/ultralytics:latest-jetson

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (OpenCV 및 PyTorch 연산을 위해 필수)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 필수 Python 패키지 설치
# ultralytics, torch, torchvision은 베이스 이미지에 포함되어 있음
RUN pip install --no-cache-dir \
    requests \
    opencv-python-headless

# 소스 코드 및 모델 복사
COPY cart_agent.py .
COPY best.pt .

# 실행 명령 (환경 변수는 실행 시 주입 권장)
CMD ["python", "cart_agent.py"]
