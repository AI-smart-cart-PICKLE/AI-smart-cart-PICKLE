import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def run_seed_sql():
    print("🌱 Seeding database from SQL file...")
    
    db_url = settings.DATABASE_URL
    if not db_url:
        print("❌ DATABASE_URL not found!")
        sys.exit(1)
        
    engine = create_engine(db_url)
    
    # SQL 파일 경로
    sql_file_path = os.path.join(os.path.dirname(__file__), "seed_data.sql")
    
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
            
        with engine.connect() as conn:
            # SQL 문장을 세미콜론(;) 기준으로 나누지 않고 통째로 실행하려면 text() 사용
            # 하지만 여러 문장이 섞여 있으므로, text()가 이를 지원하는지 DB 드라이버에 따라 다름.
            # PostgreSQL(psycopg2)은 지원함.
            conn.execute(text(sql_content))
            conn.commit()
            
        print("✅ Data seeded successfully!")
    except Exception as e:
        print(f"❌ Failed to seed data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_seed_sql()
