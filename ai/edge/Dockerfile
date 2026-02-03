# AI 프로젝트 가상환경과 동일한 Python 3.10 사용
FROM python:3.10.19-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (OpenCV 및 PyTorch 연산을 위해 필수)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 필수 Python 패키지 설치 (environment.yaml 의존성 준수)
# 엣지 에이전트 실행에 필요한 핵심 라이브러리만 설치
RUN pip install --no-cache-dir \
    torch==2.3.1 \
    torchvision \
    numpy==1.26.4 \
    ultralytics==8.4.2 \
    opencv-python-headless \
    requests

# 소스 코드 및 모델 복사
COPY cart_agent.py .
COPY best.pt .

# 실행 명령 (환경 변수는 실행 시 주입 권장)
CMD ["python", "cart_agent.py"]
