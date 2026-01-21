# 개발 및 테스트용 표준 Dockerfile (x86_64 & ARM64 호환)
# 젯슨 배포 시에는 Base Image를 'dustynv/l4t-pytorch' 등으로 변경 가능

FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치 (OpenCV 등)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# FastAPI 서버 실행 (추론 서버용)
# 포트 8000은 예시이며, docker-compose에서 매핑 필요
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "inference.main:app", "--host", "0.0.0.0", "--port", "8000"]
