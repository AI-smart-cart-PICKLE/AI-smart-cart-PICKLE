# 1단계: 빌드 환경 (Build Stage)
FROM python:3.12-slim AS builder

WORKDIR /app

# 의존성 설치를 위한 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 빌드에 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 캐싱을 위해 requirements.txt만 먼저 복사
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# 2단계: 실행 환경 (Run Stage)
FROM python:3.12-slim

WORKDIR /app

# 시스템 라이브러리 설치 (PostgreSQL 연결용)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 빌드 단계에서 설치된 패키지만 복사 (이미지 경량화 핵심)
COPY --from=builder /install /usr/local
COPY . .

# FastAPI 실행 포트 노출
EXPOSE 8000

# 컨테이너 상태 체크 (Nginx에서 backend 생존 확인용)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 서버 실행 (Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]