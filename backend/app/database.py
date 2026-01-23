# DB 연결 설정 (PostgreSQL)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. DB 주소 (사용자명:비번@주소:포트/DB이름)
# 로컬 PostgreSQL 기준 예시입니다. 본인 환경에 맞게 수정하세요!
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/pickle_db"

# 2. 엔진 생성 (DB와 연결되는 통로)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. 세션 생성 (데이터를 읽고 쓰는 작업 단위)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 모델들의 조상님 (이걸 상속받아야 테이블로 인식됨)
Base = declarative_base()

# 5. DB 세션 가져오기 (API에서 사용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()