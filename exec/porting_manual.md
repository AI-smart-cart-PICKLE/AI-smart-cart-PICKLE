# Pickle Project 포팅 매뉴얼

> **프로젝트명**: Pickle - AI 기반 스마트 장바구니 시스템
> **팀**: A202

---

## 목차

1. [개발 환경 및 버전 정보](#1-개발-환경-및-버전-정보)
2. [빌드 및 배포](#2-빌드-및-배포)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [DB 접속 정보 및 프로퍼티 파일 목록](#4-db-접속-정보-및-프로퍼티-파일-목록)
5. [외부 서비스 정보](#5-외부-서비스-정보)
6. [DB 덤프 파일](#6-db-덤프-파일)
7. [시연 시나리오](#7-시연-시나리오)

---

## 1. 개발 환경 및 버전 정보

### 1.1 서버 인프라

| 항목 | 내용 |
|------|------|
| 서버 | AWS EC2 (Ubuntu) |
| 도메인 | `i14a202.p.ssafy.io` (= `bapsim.site`) |
| SSL | Let's Encrypt (Certbot) |
| 컨테이너 런타임 | Docker + Docker Compose |
| CI/CD | GitLab CI/CD |

### 1.2 사용 기술 스택 및 버전

#### Backend (FastAPI)

| 항목 | 버전 |
|------|------|
| Python | 3.12 |
| FastAPI | 0.128.0 |
| Uvicorn | latest (standard extras) |
| SQLAlchemy | latest |
| Alembic | latest |
| psycopg2-binary | latest |
| httpx | 0.28.1 |
| python-dotenv | 1.2.1 |
| numpy | 2.4.1 |
| passlib[argon2] | latest |
| python-jose[cryptography] | latest |
| pydantic-settings | latest |
| pgvector (Python) | latest |
| mlflow | >=3.0.0 |
| boto3 | latest |

#### AI/ML 추론 서버

| 항목 | 버전 |
|------|------|
| Python | 3.10 |
| PyTorch | 2.3.1 (CUDA 12.1) |
| Ultralytics (YOLO) | 8.4.2 |
| OpenCV | >=4.8 (headless) |
| MLflow | 3.8.1 |
| FastAPI | 0.128.0 |
| NumPy | 1.26.4 |
| scikit-learn | 1.5.2 |
| pandas | 2.2.2 |
| albumentations | 1.4.10 |
| Pillow | 12.1.0 |

#### Edge Device (Jetson Orin Nano)

| 항목 | 버전 |
|------|------|
| Base Image | `nvcr.io/nvidia/l4t-jetpack:r36.4.0` (JetPack 6.0, Ubuntu 22.04) |
| Ultralytics | >=8.4.0 |
| OpenCV | >=4.8.0 (headless) |
| requests | >=2.31.0 |
| boto3 | >=1.34.0 |

#### Frontend - Web Kiosk (Vue.js)

| 항목 | 버전 |
|------|------|
| Node.js | ^20.19.0 \|\| >=22.12.0 |
| Vue.js | ^3.5.26 |
| Vue Router | ^4.6.4 |
| Pinia | ^3.0.4 |
| Axios | ^1.13.4 |
| Vite | ^7.3.0 |
| @ericblade/quagga2 | ^1.12.1 (바코드 스캔) |

#### Frontend - Mobile App (Flutter)

| 항목 | 버전 |
|------|------|
| Dart SDK | ^3.10.7 |
| Flutter | 3.38+ |
| flutter_riverpod | ^2.5.1 |
| go_router | ^14.2.7 |
| dio | ^5.9.1 |
| flutter_secure_storage | ^10.0.0 |
| google_sign_in | ^6.2.1 |
| mobile_scanner | ^7.1.4 (QR 스캔) |
| webview_flutter | ^4.13.1 |

#### 데이터베이스

| 항목 | 버전 |
|------|------|
| PostgreSQL | 16 |
| Docker Image | `pgvector/pgvector:pg16` |
| 확장: pgvector | 내장 (벡터 유사도 검색) |
| 확장: pg_trgm | 내장 (퍼지 텍스트 검색) |

#### MLOps

| 항목 | 버전 |
|------|------|
| MLflow | v3.8.1 (`ghcr.io/mlflow/mlflow:v3.8.1`) |
| Apache Airflow | 2.10.4 (`apache/airflow:2.10.4`) |
| MinIO | latest (`minio/minio`) |

#### 웹서버 / 리버스 프록시

| 항목 | 버전 |
|------|------|
| Nginx | Alpine (latest) |
| 역할 | HTTPS 종단, 리버스 프록시, 정적 파일 서빙 |

#### IDE (참고)

| 항목 | 용도 |
|------|------|
| VS Code | Backend / Frontend 개발 |
| IntelliJ IDEA / Android Studio | Flutter 모바일 앱 개발 |
| JupyterLab | AI 모델 실험 |

---

## 2. 빌드 및 배포

### 2.1 소스 클론

```bash
git clone https://lab.ssafy.com/s14-webmobile3-sub1/S14P11A202.git
cd S14P11A202
```

### 2.2 환경 변수 파일 생성

`.env.example`을 참고하여 프로젝트 루트에 `.env` 파일을 생성합니다.

```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
vi .env
```

필수 환경 변수는 [3. 환경 변수 설정](#3-환경-변수-설정)을 참조하세요.

### 2.3 SSL 인증서 설정

#### 운영 환경 (Let's Encrypt)

```bash
# certbot 설치 및 인증서 발급
sudo apt install certbot
sudo certbot certonly --standalone -d bapsim.site -d www.bapsim.site

# 인증서 경로: /etc/letsencrypt/live/bapsim.site/
# .env 파일에 설정
SSL_CERT_PATH=/etc/letsencrypt
```

#### 로컬 개발 환경 (자체 서명)

```bash
mkdir -p certs/live/bapsim.site
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/live/bapsim.site/privkey.pem \
  -out certs/live/bapsim.site/fullchain.pem \
  -subj "//CN=bapsim.site"

# hosts 파일에 추가
echo "127.0.0.1 bapsim.site" >> /etc/hosts
```

### 2.4 Docker Compose 빌드 및 실행

#### 운영 환경 (EC2, CPU 모드)

```bash
# 이미지 빌드 및 실행
docker compose --profile cpu up -d --build

# 로그 확인
docker compose logs -f
```

#### 개발 환경 (GPU 사용)

```bash
# NVIDIA GPU가 있는 환경
docker compose --profile dev up -d --build
```

#### 기본 실행 (AI 서버 제외)

```bash
docker compose up -d --build
```

### 2.5 서비스 구성 및 포트

| 서비스 | 컨테이너명 | 포트(호스트:컨테이너) | 비고 |
|--------|-----------|---------------------|------|
| PostgreSQL | `postgres_db` | 5432:5432 | pgvector 확장 포함 |
| MinIO | `minio_storage` | 9000:9000, 9001:9001 | S3 호환 오브젝트 스토리지 |
| MinIO Init | `minio_init` | - | 버킷 자동 생성 후 종료 |
| MLflow | `mlflow_server` | 5001:5000 | 실험 추적 UI |
| Airflow | `airflow_standalone` | 8081:8080 | DAG 파이프라인 관리 |
| Backend API | `fastapi_backend` | 8000:8000 | FastAPI 서버 |
| AI Inference (CPU) | `ai_inference` | 8001:8000 | YOLO 추론 (profile: cpu) |
| AI Inference (GPU) | `ai_inference_gpu` | 8001:8000 | YOLO 추론 (profile: dev/gpu) |
| Nginx | `nginx_gateway` | 80:80, 443:443 | 리버스 프록시 + 정적 파일 |

### 2.6 DB 초기화

Docker Compose 최초 실행 시 `init-db.sh`가 자동으로 실행되어 3개의 데이터베이스를 생성합니다:

- `airflow` - Airflow 메타데이터
- `mlflow` - MLflow 실험 추적
- `app_db` - 비즈니스 로직 (pgvector 확장 활성화)

#### 스키마 초기화 (수동)

```bash
# 전체 스키마 초기화 (기존 데이터 삭제 후 재생성)
docker compose exec -T db psql -U admin -d app_db < full_db_init.sql

# 시드 데이터 삽입
docker compose exec -T db psql -U admin -d app_db < backend/scripts/seed_data.sql
```

#### Alembic 마이그레이션

```bash
# 컨테이너 내부에서 실행
docker compose exec backend alembic upgrade head

# 새 마이그레이션 생성
docker compose exec backend alembic revision --autogenerate -m "description"
```

### 2.7 Frontend 빌드

#### Web Kiosk (Vue.js)

```bash
cd frontend/cart
npm ci
npm run build
# 빌드 결과: frontend/cart/dist/
```

빌드된 정적 파일은 `frontend/dist/`로 복사되어 Nginx에서 서빙됩니다.

#### Mobile App (Flutter)

```bash
cd frontend/mobile-app
flutter pub get
flutter build apk --release
```

모바일 앱의 `.env` 파일에 API URL 설정이 필요합니다:

```
API_URL=https://bapsim.site/api/
```

### 2.8 CI/CD 파이프라인 (GitLab CI)

`.gitlab-ci.yml` 기반으로 `master` 브랜치 푸시 시 자동 배포됩니다.

#### 파이프라인 스테이지

| Stage | Job | 트리거 조건 | 설명 |
|-------|-----|-----------|------|
| build | `build-backend` | `backend/**/*` 변경 | Backend Docker 이미지 빌드 → Docker Hub Push |
| build | `build-ai` | `ai/**/*` 변경 | AI Docker 이미지 빌드 → Docker Hub Push |
| build | `build-frontend` | `frontend/**/*` 변경 | Vue.js 빌드 (Node 20 Alpine) |
| build | `build-airflow` | `mlops/**/*` 변경 | Airflow Docker 이미지 빌드 → Docker Hub Push |
| deploy | `deploy` | master 브랜치 | EC2에 SSH 접속하여 배포 |

#### GitLab CI/CD Variables (필수 등록)

| Variable | 설명 |
|----------|------|
| `DOCKER_USERNAME` | Docker Hub 사용자명 |
| `DOCKER_PASSWORD` | Docker Hub Access Token |
| `EC2_HOST` | EC2 퍼블릭 IP/도메인 (예: `i14a202.p.ssafy.io`) |
| `EC2_USER` | SSH 사용자 (예: `ubuntu`) |
| `SSH_PRIVATE_KEY` | EC2 접속용 SSH Private Key (전체 내용) |
| `DB_USER` | PostgreSQL 사용자 |
| `DB_PASSWORD` | PostgreSQL 비밀번호 |
| `MINIO_ROOT_USER` | MinIO 관리자 ID |
| `MINIO_ROOT_PASSWORD` | MinIO 관리자 비밀번호 |
| `SECRET_KEY` | JWT 서명 비밀키 |
| `KAKAO_ADMIN_KEY` | 카카오 Admin Key |
| `KAKAO_REST_API_KEY` | 카카오 REST API Key |
| `KAKAO_REDIRECT_URI` | 카카오 로그인 콜백 URI |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | Google OAuth 콜백 URI |
| `SMTP_HOST` | SMTP 메일 서버 주소 |
| `SMTP_PORT` | SMTP 포트 |
| `SMTP_USER` | SMTP 발신 이메일 |
| `SMTP_PASSWORD` | SMTP 앱 비밀번호 |
| `FRONTEND_URL` | 프론트엔드 URL |
| `AIRFLOW_BASE_URL` | Airflow 베이스 URL |
| `SSL_CERT_PATH` | SSL 인증서 경로 |
| `BASE_URL` | Backend API 베이스 URL |

### 2.9 배포 시 특이사항

1. **DB 데이터 보존**: 배포 시 `alembic_version` 테이블만 초기화하고, 현재 모델 기준으로 새 마이그레이션을 생성한 뒤 `alembic stamp head`로 표시합니다. 실제 데이터는 삭제되지 않습니다.

2. **Frontend fallback**: `frontend/dist/`가 비어 있으면 `frontend/web-kiosk/dist/`에서 자동 복사됩니다.

3. **Docker 이미지 레지스트리**: Docker Hub (`srogsrogi/smart-cart-*`)를 사용합니다.

4. **AI 서버 프로파일**:
   - EC2(CPU): `docker compose --profile cpu up -d`
   - GPU 장비: `docker compose --profile dev up -d` (NVIDIA GPU 필요)

5. **Backend 메모리 제한**: 6GB, CPU 2코어로 제한되어 있습니다.

6. **AI 서버 메모리 제한**: CPU 모드 4GB, GPU 모드 8GB.

7. **MinIO 버킷**: `mlflow`, `data`, `smart-cart-mlops` 3개 버킷이 자동 생성됩니다. `smart-cart-mlops/uncertain-images`는 public download 설정입니다.

---

## 3. 환경 변수 설정

### 3.1 루트 `.env` (Backend + Docker Compose 공용)

```env
# --- DB ---
DB_USER=admin
DB_PASSWORD=<비밀번호>
DATABASE_URL=postgresql://admin:<비밀번호>@localhost:5432/app_db

# --- MinIO (S3 호환 스토리지) ---
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=<비밀번호>
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=<비밀번호>
MINIO_BUCKET_NAME=smart-cart

# --- MLflow ---
MLFLOW_ARTIFACT_ROOT=s3://mlflow/

# --- Docker Hub ---
DOCKER_USERNAME=<Docker Hub 사용자명>
DOCKER_PASSWORD=<Docker Hub Access Token>

# --- EC2 배포 ---
EC2_HOST=i14a202.p.ssafy.io
EC2_USER=ubuntu

# --- 앱 설정 ---
BACKEND_PORT=8000
MLFLOW_PORT=5001
AIRFLOW_BASE_URL=https://bapsim.site/airflow
SSL_CERT_PATH=/etc/letsencrypt
AI_INFERENCE_URL=http://ai_inference:8000   # CPU 모드
# AI_INFERENCE_URL=http://ai_inference_gpu:8000  # GPU 모드
BASE_URL=https://bapsim.site/api

# --- 소셜 로그인 ---
KAKAO_REST_API_KEY=<카카오 REST API 키>
KAKAO_REDIRECT_URI=https://bapsim.site/api/auth/kakao/callback
KAKAO_ADMIN_KEY=<카카오 Admin 키>

GOOGLE_CLIENT_ID=<Google OAuth Client ID>
GOOGLE_CLIENT_SECRET=<Google OAuth Client Secret>
GOOGLE_REDIRECT_URI=https://bapsim.site/api/auth/google/callback

# --- SMTP (비밀번호 재설정 메일) ---
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<발신 이메일>
SMTP_PASSWORD=<Google 앱 비밀번호>
FRONTEND_URL=https://bapsim.site

# --- AI 불확실 이미지 수집 ---
UNCERTAIN_CONFIDENCE_THRESHOLD=0.5
UNCERTAIN_UPLOAD_INTERVAL=5

# --- JWT ---
SECRET_KEY=<JWT 서명용 비밀키>
```

### 3.2 Frontend Cart 환경 변수

| 파일 | 용도 | 내용 |
|------|------|------|
| `frontend/cart/.env.dev` | 개발 | `VITE_BACKEND_URL=https://bapsim.site` |
| `frontend/cart/.env.prod` | 운영 | (빈 파일 - Nginx 프록시 사용) |
| `frontend/cart/.env.example` | 템플릿 | `VITE_BACKEND_URL=http://localhost:8000` |

### 3.3 Mobile App 환경 변수

| 파일 | 내용 |
|------|------|
| `frontend/mobile-app/.env` | `API_URL=https://bapsim.site/api/` |

---

## 4. DB 접속 정보 및 프로퍼티 파일 목록

### 4.1 DB 접속 정보

| 항목 | 값 |
|------|-----|
| DBMS | PostgreSQL 16 + pgvector |
| Host (컨테이너 내부) | `db:5432` |
| Host (외부 접속) | `i14a202.p.ssafy.io:5432` |
| 사용자 | `admin` |
| 비밀번호 | `.env`의 `DB_PASSWORD` 참조 |
| 데이터베이스 (앱) | `app_db` |
| 데이터베이스 (MLflow) | `mlflow` |
| 데이터베이스 (Airflow) | `airflow` |

### 4.2 데이터베이스 스키마 (ERD)

`app_db` 데이터베이스에는 다음 테이블이 존재합니다:

| 테이블 | 설명 |
|--------|------|
| `app_user` | 회원 (LOCAL/GOOGLE/KAKAO 소셜 로그인 지원) |
| `password_reset_token` | 비밀번호 재설정 토큰 |
| `product_category` | 상품 카테고리 (zone_code로 매장 구역 매핑) |
| `product` | 상품 (pgvector 1536차원 임베딩 포함) |
| `recipe` | 레시피 (pgvector 1536차원 임베딩 포함) |
| `recipe_ingredient` | 레시피-상품 연결 (M:N) |
| `saved_recipe` | 사용자 저장 레시피 |
| `cart_device` | 카트 기기 (device_code로 식별) |
| `cart_session` | 카트 세션 (ACTIVE → CHECKOUT_REQUESTED → PAID/CANCELLED) |
| `cart_item` | 카트 내 상품 (세션+상품 UNIQUE) |
| `cart_detection_log` | AI 감지 로그 (ADD/REMOVE 액션) |
| `payment_method` | 결제 수단 (CARD/KAKAO_PAY) |
| `payment` | 결제 정보 (PENDING → APPROVED/FAILED/CANCELLED) |
| `ledger_entry` | 가계부 (결제 완료 시 자동 생성) |

#### 커스텀 Enum 타입

- `user_provider`: LOCAL, GOOGLE, KAKAO
- `cart_session_status`: ACTIVE, CHECKOUT_REQUESTED, PAID, CANCELLED
- `detection_action_type`: ADD, REMOVE
- `payment_method_type`: CARD, KAKAO_PAY
- `pg_provider_type`: KAKAO_PAY, CARD_PG
- `payment_status`: PENDING, APPROVED, FAILED, CANCELLED
- `ledger_category`: GROCERY, MEAT, DAIRY, BEVERAGE, SNACK, HOUSEHOLD, ETC

### 4.3 프로퍼티 파일 목록

| 파일 경로 | 설명 |
|----------|------|
| `.env` | 전체 환경 변수 (DB, MinIO, 소셜 로그인, SMTP 등) |
| `.env.example` | 환경 변수 템플릿 |
| `backend/app/core/config.py` | Backend 설정 클래스 (Settings) |
| `backend/app/database.py` | SQLAlchemy DB 연결 설정 |
| `backend/alembic.ini` | Alembic 마이그레이션 설정 |
| `backend/app/models.py` | ORM 모델 정의 |
| `docker-compose.yml` | Docker 서비스 구성 |
| `nginx-ssl-prod.conf` | Nginx 리버스 프록시 설정 |
| `init-db.sh` | DB 초기화 스크립트 (3개 DB 생성) |
| `frontend/cart/.env.dev` | Frontend 개발 환경 변수 |
| `frontend/cart/.env.prod` | Frontend 운영 환경 변수 |
| `frontend/mobile-app/.env` | Flutter 앱 환경 변수 |

---

## 5. 외부 서비스 정보

### 5.1 카카오 로그인 / 카카오페이

| 항목 | 설명 |
|------|------|
| 서비스 | Kakao Developers |
| 가입 URL | https://developers.kakao.com |
| 사용 기능 | 카카오 로그인 (OAuth), 카카오페이 단건 결제 |
| 필요 키 | REST API Key, Admin Key |
| 설정 위치 | `.env`의 `KAKAO_REST_API_KEY`, `KAKAO_ADMIN_KEY`, `KAKAO_REDIRECT_URI` |
| 테스트 CID | `TC0ONETIME` (카카오페이 테스트용 일반 결제) |
| 콜백 URI | `https://bapsim.site/api/auth/kakao/callback` |

**설정 절차**:
1. https://developers.kakao.com 에서 애플리케이션 생성
2. 앱 키 > REST API Key, Admin Key 복사
3. 카카오 로그인 활성화, Redirect URI 등록
4. 카카오페이 결제 활성화 (테스트 모드)
5. 동의항목에서 이메일, 닉네임 수집 설정

### 5.2 Google 소셜 로그인

| 항목 | 설명 |
|------|------|
| 서비스 | Google Cloud Console |
| 가입 URL | https://console.cloud.google.com |
| 사용 기능 | Google OAuth 2.0 로그인 |
| 필요 키 | Client ID, Client Secret |
| 설정 위치 | `.env`의 `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` |
| 콜백 URI | `https://bapsim.site/api/auth/google/callback` |

**설정 절차**:
1. Google Cloud Console > API 및 서비스 > 사용자 인증 정보
2. OAuth 2.0 클라이언트 ID 생성 (웹 애플리케이션)
3. 승인된 리디렉션 URI에 콜백 주소 등록
4. Client ID, Client Secret 복사

### 5.3 SMTP (Gmail)

| 항목 | 설명 |
|------|------|
| 서비스 | Gmail SMTP |
| 용도 | 비밀번호 재설정 이메일 발송 |
| 호스트 | `smtp.gmail.com` |
| 포트 | `587` (TLS) |
| 설정 위치 | `.env`의 `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` |

**설정 절차**:
1. Google 계정 > 보안 > 2단계 인증 활성화
2. 앱 비밀번호 생성 (메일용)
3. 생성된 16자리 앱 비밀번호를 `SMTP_PASSWORD`에 입력

> **참고**: SSAFY 네트워크에서는 SMTP가 차단될 수 있습니다. SendGrid 등 HTTP API 기반 이메일 서비스로 대체를 권장합니다.

### 5.4 Docker Hub

| 항목 | 설명 |
|------|------|
| 서비스 | Docker Hub |
| 용도 | CI/CD에서 빌드한 Docker 이미지 저장/배포 |
| 설정 위치 | `.env`의 `DOCKER_USERNAME`, `DOCKER_PASSWORD` |

**이미지 목록**:
- `<username>/smart-cart-backend:latest`
- `<username>/smart-cart-ai:latest`
- `<username>/smart-cart-airflow:latest`

### 5.5 MinIO (자체 호스팅, S3 호환)

| 항목 | 설명 |
|------|------|
| 용도 | MLflow 아티팩트 저장, 학습 데이터 관리, 불확실 이미지 수집 |
| 콘솔 접속 | `http://<서버IP>:9001` |
| API 엔드포인트 | `http://<서버IP>:9000` |
| 버킷 | `mlflow`, `data`, `smart-cart-mlops` |

---

## 6. DB 덤프 파일

### 6.1 스키마 초기화 파일

- **`full_db_init.sql`** - 전체 테이블 DROP 후 최신 스키마로 재생성 (16개 테이블, 7개 Enum 타입, 인덱스 포함)

### 6.2 시드 데이터 파일

- **`backend/scripts/seed_data.sql`** - 초기 데이터 (카테고리, 상품, 레시피, 레시피 재료 매핑, 카트 디바이스)

### 6.3 DB 덤프 생성 방법

```bash
# 전체 DB 덤프 (스키마 + 데이터)
docker compose exec db pg_dump -U admin -d app_db --no-owner --no-acl > db_dump_$(date +%Y%m%d).sql

# 스키마만 덤프
docker compose exec db pg_dump -U admin -d app_db --schema-only --no-owner > schema_only.sql

# 데이터만 덤프
docker compose exec db pg_dump -U admin -d app_db --data-only --no-owner > data_only.sql
```

### 6.4 DB 복원 방법

```bash
# DB 접속 후 복원
docker compose exec -T db psql -U admin -d app_db < db_dump_20260209.sql
```

---

## 7. 시연 시나리오

### 시나리오 개요

스마트 장바구니(Pickle)의 전체 사용자 플로우를 시연합니다.
- **모바일 앱**: 회원가입/로그인, QR 연동, 가계부 확인
- **웹 키오스크 (카트 화면)**: 장바구니 실시간 업데이트, AI 추천, 결제
- **Jetson 엣지 디바이스**: 실시간 YOLO 상품 인식

---

### STEP 1. 모바일 앱 - 회원가입 및 로그인

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 1-1 | 로그인 화면 | 앱 실행 | Pickle 앱을 실행합니다. |
| 1-2 | 로그인 화면 | "카카오로 시작하기" 클릭 | 카카오 소셜 로그인 페이지로 이동합니다. |
| 1-3 | 카카오 로그인 | 카카오 계정 입력 후 로그인 | 카카오 인증 완료 후 앱으로 리다이렉트됩니다. |
| 1-4 | 메인 화면 | 자동 진입 | 로그인 성공 시 메인 화면이 표시됩니다. |

> **대안**: "구글로 시작하기" 또는 이메일 회원가입도 가능합니다.

---

### STEP 2. 모바일 앱 - 카트 연동 (QR 페어링)

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 2-1 | 메인 화면 | "장보기 시작" 버튼 클릭 | QR 스캔 카메라가 활성화됩니다. |
| 2-2 | QR 스캔 화면 | 카트의 QR 코드를 스캔 | 카트 디바이스와 사용자 계정이 연동됩니다. |
| 2-3 | 연동 완료 | 자동 전환 | "장보기가 시작되었습니다" 메시지와 함께 카트 세션이 ACTIVE 상태가 됩니다. |

---

### STEP 3. 웹 키오스크 - QR 페어링 확인

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 3-1 | 페어링 화면 (`/pair`) | 카트 화면 초기 상태 | QR코드가 표시되어 있습니다. |
| 3-2 | 대시보드 (`/`) | 자동 전환 | 모바일 앱에서 QR 스캔 시 자동으로 대시보드로 이동합니다. |
| 3-3 | 대시보드 | 장바구니 패널 확인 | 빈 장바구니 상태, 총액 0원이 표시됩니다. |

---

### STEP 4. 상품 인식 - YOLO AI 실시간 감지

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 4-1 | 카트 카메라 | 상품을 카트에 넣기 | Jetson 카메라가 상품을 실시간 감지합니다. |
| 4-2 | 웹 키오스크 | 자동 업데이트 | 감지된 상품이 장바구니 패널에 자동으로 추가됩니다. (상품명, 가격, 수량 표시) |
| 4-3 | 웹 키오스크 | 추가 상품 넣기 | 여러 상품을 넣으면 실시간으로 목록과 총액이 업데이트됩니다. |
| 4-4 | 웹 키오스크 | 상품 빼기 | 카트에서 상품을 빼면 AI가 REMOVE를 감지하여 자동 차감됩니다. |

**시연용 인식 대상 상품**: 스팸, 토마토 케찹, 스파게티면, 살코기참치, 3분카레, 딸기잼, 신라면, 펩시 제로슈거

---

### STEP 5. AI 레시피 추천

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 5-1 | 웹 키오스크 | 추천 패널 확인 | 장바구니에 상품이 추가되면 AI 추천 패널이 활성화됩니다. |
| 5-2 | 추천 패널 | 레시피 카드 확인 | pgvector 임베딩 유사도 기반으로 추천된 레시피가 표시됩니다. |
| 5-3 | 추천 패널 | 레시피 카드 클릭 | 필요한 재료 목록이 표시됩니다. 이미 보유한 재료는 체크, 부족한 재료는 별도 표시됩니다. |

**시연 예시**:
- **스팸 + 신라면** 투입 → "의정부식 부대찌개" 추천 (부족 재료: 김치, 두부, 대파)
- **참치** 투입 → "참치 김치찌개" 추천 (부족 재료: 김치, 양파)
- **스파게티면 + 케찹** 투입 → "나폴리탄 스파게티" 추천 (부족 재료: 양파, 마늘)

---

### STEP 6. 결제 (카카오페이)

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 6-1 | 웹 키오스크 | 하단 "결제하기" 버튼 클릭 | 결제 준비 API가 호출됩니다. |
| 6-2 | 웹 키오스크 | QR 코드 표시 | 카카오페이 결제 QR이 화면에 표시됩니다. |
| 6-3 | 모바일 (카카오톡) | QR 스캔 또는 링크 클릭 | 카카오페이 결제 화면으로 이동합니다. |
| 6-4 | 카카오페이 | 결제 비밀번호 입력 | 결제를 승인합니다. (테스트 모드: `TC0ONETIME`) |
| 6-5 | 결제 완료 페이지 | "결제 완료" 확인 | 결제 성공 시 HTML 페이지가 표시되고 3초 후 자동 닫힘. |
| 6-6 | 웹 키오스크 | 세션 종료 | 카트 세션이 PAID 상태로 변경되고 대시보드가 초기화됩니다. |

---

### STEP 7. 모바일 앱 - 가계부 확인

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 7-1 | 모바일 앱 | "가계부" 탭 클릭 | 결제 완료 후 자동 등록된 지출 내역을 확인합니다. |
| 7-2 | 가계부 화면 | 내역 확인 | 날짜, 금액, 카테고리(GROCERY/MEAT 등)가 표시됩니다. |
| 7-3 | 가계부 화면 | 월별/기간별 통계 확인 | 지출 추이를 그래프로 확인할 수 있습니다. |

---

### STEP 8. (부가) 관리자 기능

| 순서 | 화면 | 동작 | 설명 |
|------|------|------|------|
| 8-1 | Airflow UI | `https://bapsim.site/airflow/` 접속 | 모델 재학습 파이프라인 모니터링 |
| 8-2 | MLflow UI | `https://bapsim.site/mlflow/` 접속 | 학습 실험 결과, 모델 버전 관리 |
| 8-3 | MinIO Console | `http://<서버>:9001` 접속 | 학습 데이터, 불확실 이미지 확인 |

---

### Nginx 라우팅 요약

| URL 패턴 | 목적지 | 설명 |
|----------|--------|------|
| `/` | Nginx 정적 파일 | Vue.js 웹 키오스크 |
| `/api/*` | `backend:8000` | FastAPI Backend |
| `/airflow/*` | `airflow:8080` | Airflow 웹 UI |
| `/mlflow/*` | `mlflow:5000` | MLflow 웹 UI |
| `/minio/*` | `minio:9000` | MinIO S3 API |
