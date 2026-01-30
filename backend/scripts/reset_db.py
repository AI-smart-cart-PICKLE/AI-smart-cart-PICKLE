import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def reset_database():
    print("🗑️ Database reset initiated...")
    
    # DB URL 확인
    db_url = settings.DATABASE_URL
    if not db_url:
        print("❌ DATABASE_URL not found!")
        sys.exit(1)
        
    engine = create_engine(db_url)
    
    # Drop all tables and types logic
    # CASCADE를 사용하여 의존성 있는 객체들도 모두 삭제
    drop_sql = text("""
    DO $$ DECLARE
        r RECORD;
    BEGIN
        -- 1. Drop all tables
        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
        END LOOP;
        
        -- 2. Drop all enums/types
        FOR r IN (SELECT typname FROM pg_type t JOIN pg_namespace n ON t.typnamespace = n.oid WHERE n.nspname = 'public' AND t.typtype = 'e') LOOP
            EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
        END LOOP;
        
        -- 3. Clear alembic_version table just in case
        EXECUTE 'DROP TABLE IF EXISTS alembic_version CASCADE';
    END $$;
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(drop_sql)
            conn.commit()
        print("✅ Database successfully cleared (Tables & Types dropped).")
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
