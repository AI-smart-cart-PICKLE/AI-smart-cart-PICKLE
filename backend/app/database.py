import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 환경 변수에서 DB 주소를 가져옵니다. (Docker Compose에서 설정됨)
# 없으면 로컬 기본값 사용 (User: admin, PW: password123, DB: postgres)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:password123@localhost:5432/postgres"
)

# SQLite 등 다른 DB를 쓸 때를 대비한 예외처리 (Postgres는 connect_args 불필요)
connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
