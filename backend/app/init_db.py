# init_db.py
from sqlalchemy import text
from app.database import SessionLocal

def init_db():
    db = SessionLocal()
    try:
        # 1. 벡터 확장기능 켜기
        print("DB에 벡터 기능을 켜는 중...")
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        print("✅ 성공! pgvector 기능이 활성화되었습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print("혹시 DB가 켜져 있는지, .env 설정이 맞는지 확인해주세요.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()