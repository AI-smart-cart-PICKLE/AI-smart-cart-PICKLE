
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pickle")

def insert_dummy_session():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("--- 🛠️ DB 더미 데이터 삽입 시작 ---")
        
        # 1. 테스트용 디바이스 확인/생성
        conn.execute(text("""
            INSERT INTO cart_device (cart_device_id, device_code)
            VALUES (1, 'CART-DEVICE-001')
            ON CONFLICT (cart_device_id) DO NOTHING;
        """))
        
        # 2. 테스트용 유저 확인/생성 (ID 15번이 아까 로그에 있었으므로)
        conn.execute(text("""
            INSERT INTO app_user (user_id, email, nickname, provider)
            VALUES (15, 'test@example.com', '테스터', 'LOCAL')
            ON CONFLICT (user_id) DO NOTHING;
        """))

        # 3. 1번 세션 강제 생성 (ACTIVE 상태)
        conn.execute(text("""
            INSERT INTO cart_session (cart_session_id, cart_device_id, user_id, status, started_at)
            VALUES (1, 1, 15, 'ACTIVE', NOW())
            ON CONFLICT (cart_session_id) DO UPDATE 
            SET status = 'ACTIVE', user_id = 15;
        """))
        
        # 4. 1번 세션에 더미 상품 추가
        # 상품 ID 1번 (스팸)이 seed_data에 있었음
        conn.execute(text("""
            INSERT INTO cart_item (cart_session_id, product_id, quantity, unit_price)
            VALUES (1, 1, 2, 5200)
            ON CONFLICT DO NOTHING;
        """))
        
        conn.commit()
        print("✅ ID 1번에 대한 더미 세션 및 상품 삽입 완료!")

if __name__ == "__main__":
    insert_dummy_session()
