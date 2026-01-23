from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from contextlib import asynccontextmanager

# 데이터베이스 테이블 생성 (서버 시작 시)
# 주의: 프로덕션에서는 Alembic과 같은 마이그레이션 도구를 사용하는 것이 좋습니다.
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행될 로직
    print("Server is starting...")
    yield
    # 종료 시 실행될 로직
    print("Server is shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Smart Cart Backend is running!"}

@app.get("/health")
def health_check():
    """
    Docker Healthcheck 및 로드밸런서 상태 확인용 엔드포인트
    """
    return {"status": "ok"}

@app.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    """
    데이터베이스 연결 테스트
    """
    try:
        # 간단한 쿼리 실행 (PostgreSQL 버전 확인)
        result = db.execute("SELECT version();").fetchone()
        return {"status": "connected", "version": result[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
