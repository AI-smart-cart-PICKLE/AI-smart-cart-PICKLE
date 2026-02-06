import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# .env 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def reset():
    with engine.begin() as conn:
        conn.execute(text("UPDATE product SET embedding = NULL"))
        conn.execute(text("UPDATE recipe SET embedding = NULL"))
        print("✅ product 및 recipe 테이블의 embedding이 NULL로 초기화되었습니다.")

if __name__ == "__main__":
    reset()
