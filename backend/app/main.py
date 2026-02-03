from dotenv import load_dotenv
load_dotenv() # .env 파일을 찾아서 환경변수로 로드함
# 앱 실행 진입점
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from . import models  # 우리가 만든 models.py를 가져와야 테이블을 인식합니다!
from .routers import cart, payment, user, auth, product, ledger, recommendation, recipe # 라우터 파일들 임포트

# ★ 핵심: 서버 시작할 때 DB에 없는 테이블을 자동으로 생성함
# models.py에 정의된 클래스들을 보고 매핑합니다.
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pickle Project API",
    description="스마트 카트 및 추천/결제 서비스 API",
    version="1.0.0"
)

import os

# CORS 
# 개발 환경에서는 모든 출처 허용 ("*")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 곳에서 접속 허용 (보안상 개발때만 사용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP Method 허용 (GET, POST 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록 (만들어둔 API 연결)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(payment.router)
app.include_router(ledger.router)
app.include_router(recommendation.router)
app.include_router(recipe.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Pickle! 서버가 정상 작동 중입니다."}

@app.get("/health")
def health():
    return {"status": "ok"}