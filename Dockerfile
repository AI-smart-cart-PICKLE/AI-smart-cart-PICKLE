# 1. Base Image: 파이썬 3.11
FROM python:3.11-slim

# 2. 필수 패키지 설치 (OpenCV 구동용 라이브러리 포함)
# libgl1-mesa-glx: OpenCV 에러 방지용
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 실행 명령어
# -u 옵션: 파이썬 로그가 버퍼링 없이 바로 출력되게 함 (디버깅용)
CMD ["python", "-u", "main.py"]