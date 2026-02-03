# JetPack 6.0 (Ubuntu 22.04) 환경에 최적화된 NVIDIA 공식 PyTorch 이미지 사용
FROM nvcr.io/nvidia/l4t-jetpack:r36.4.0

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 라이브러리 설치
# 22.04 기반이므로 libffi.so.8 문제가 발생하지 않습니다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Ultralytics 및 필수 패키지 설치
# (NVIDIA 이미지는 이미 torch가 깔려있으므로 ultralytics만 추가)
RUN pip3 install --no-cache-dir ultralytics requests opencv-python-headless

# 소스 코드 및 모델 복사
COPY cart_agent.py .
COPY best.pt .

# 실행 명령어
CMD ["python3", "cart_agent.py"]