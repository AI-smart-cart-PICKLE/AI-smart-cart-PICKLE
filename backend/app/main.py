import logging
import os
from dotenv import load_dotenv

# 1. 환경 변수 로드 (가장 먼저 실행)
load_dotenv()

# 2. FastAPI 및 관련 라이브러리 임포트
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# 3. 내부 모듈 임포트 (Database, Models, Handlers)
from app.database import engine, Base
from app import models
from app.core.exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler
)

# 4. 라우터 임포트
from app.routers import (
    cart,
    payment,
    user,
    auth,
    product,
    ledger,
    recommendation,
    recipe,
    admin
)

# =========================================================
# ⚙️ 설정 및 초기화
# =========================================================

# 전역 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# DB 테이블 자동 생성 (필요 시 주석 해제)
# models.py에 정의된 클래스들을 보고 매핑합니다.
# Base.metadata.create_all(bind=engine)

# FastAPI 앱 초기화
app = FastAPI(
    title="Pickle Project API",
    description="스마트 카트 및 추천/결제 서비스 API (SSAFY 14th Project)",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 주소
    redoc_url="/redoc" # ReDoc 주소
)

# =========================================================
# 🛡️ 미들웨어 & 예외 핸들러 (Middleware & Handlers)
# =========================================================

# CORS 설정 (개발 환경: 모든 출처 허용)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE 등 모든 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 전역 예외 핸들러 등록 (순서 중요)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# =========================================================
# 🌐 라우터 등록 (Router Inclusion)
# =========================================================

# 1. 인증 및 사용자 관련
app.include_router(user.auth_router, prefix="/api")  # 회원가입, 로그인 등
app.include_router(user.user_router, prefix="/api")  # 내 정보 조회 등
app.include_router(auth.router, prefix="/api")       # 토큰 갱신, QR 로그인 등

# 2. 핵심 도메인 (상품, 카트, 결제, 추천)
app.include_router(product.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(payment.router, prefix="/api")
app.include_router(recommendation.router, prefix="/api")
app.include_router(recipe.router, prefix="/api")

# 3. 기타 (가계부, 관리자)
app.include_router(ledger.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# =========================================================
# 🚀 헬스 체크 (Health Check)
# =========================================================

@app.get("/")
def read_root():
    return {
        "project": "Pickle",
        "status": "Running",
        "message": "서버가 정상 작동 중입니다. /docs로 이동하여 API를 테스트하세요."
    }

@app.get("/health")
def health():
    return {"status": "ok"}