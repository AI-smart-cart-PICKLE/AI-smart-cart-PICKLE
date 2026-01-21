# Backend (Main API Server)

이 디렉토리는 서비스의 핵심 비즈니스 로직을 담당하는 **Main API Server**입니다.



## 1. 디렉토리 구조

- **`app/`**: FastAPI 소스 코드 메인 패키지
  - **`main.py`**: 앱 진입점 및 FastAPI 설정
  - **`routers/`**: API 엔드포인트 모음
  - **`models.py`**: SQLAlchemy DB 모델 정의
  - **`schemas.py`**: Pydantic DTO 정의
  - **`database.py`**: DB 연결 세션 관리
- **`Dockerfile`**: 백엔드 서버 컨테이너 빌드 파일
- **`requirements.txt`**: 의존성 패키지 목록



## 2. 개발 환경

- **Language**: Python 3.12.9
- **Framework**: FastAPI 0.128.0
- **Database**: PostgreSQL 16.x (w/ pgvector)
- **Storage**: MinIO (S3 Compatible) 7.2.20



## 3. 실행 가이드

