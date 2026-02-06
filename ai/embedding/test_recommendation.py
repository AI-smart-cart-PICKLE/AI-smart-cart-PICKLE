import os
import sys
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path

# 프로젝트 루트의 .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_scenario(name, product_ids):
    print(f"\n=== Testing Scenario: {name} ===")
    db = SessionLocal()
    try:
        # 1. 테스트용 임시 카트 세션 생성 (ID 1은 기본 기기)
        res = db.execute(text("INSERT INTO cart_session (cart_device_id, status) VALUES (1, 'ACTIVE') RETURNING cart_session_id"))
        session_id = res.fetchone()[0]
        
        # 2. 카트에 상품 담기
        for pid in product_ids:
            p = db.execute(text("SELECT price FROM product WHERE product_id = :id"), {"id": pid}).fetchone()
            if p:
                db.execute(text("INSERT INTO cart_item (cart_session_id, product_id, quantity, unit_price) VALUES (:sid, :pid, 1, :price)"),
                           {"sid": session_id, "pid": pid, "price": p[0]})
        
        db.commit()
        print(f"Cart created (ID: {session_id}) with products: {product_ids}")
        
        # 3. 추천 API 호출
        try:
            api_url = f"http://localhost:8000/api/recommendations/by-cart/{session_id}"
            api_res = requests.get(api_url)
            if api_res.status_code == 200:
                recs = api_res.json()
                print(f"AI Recommendations ({len(recs)} found):")
                for i, r in enumerate(recs):
                    missing = [m['name'] for m in r.get('missing_ingredients', [])]
                    print(f"  {i+1}. {r['title']} | Missing: {missing}")
            else:
                print(f"API Error: {api_res.status_code}")
        except Exception as e:
            print(f"Connection error: {e}")
            print("Is the backend server running at http://localhost:8000?")

    finally:
        # Cleanup
        db.execute(text("DELETE FROM cart_session WHERE cart_session_id = :id"), {"id": session_id})
        db.commit()
        db.close()

if __name__ == "__main__":
    # 시나리오 테스트
    test_scenario("Western (Pasta + Ketchup)", [3, 2])
    test_scenario("Brunch (Bread + Milk + Egg)", [500, 9, 10])
    test_scenario("Korean Stew (Spam + Ramen)", [1, 7])